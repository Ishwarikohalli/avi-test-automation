import logging
import concurrent.futures

logger = logging.getLogger(__name__)

class TestRunner:
    def __init__(self, api_client):
        self.api_client = api_client
        self.test_results = []
    
    def execute_test_case(self, test_config):
        """Execute a single test case"""
        logger.info(f"Executing test case: '{test_config['name']}'")
        result = {
            'test_name': test_config['name'],
            'stages': {},
            'success': True
        }
        
        try:
            # Stage 1: Pre-Fetcher
            logger.info("[STAGE 1: Pre-Fetcher]")
            pre_fetch_results = self._execute_pre_fetcher(test_config.get('pre_fetcher', []))
            result['stages']['pre_fetcher'] = pre_fetch_results
            
            # Extract VS UUID from pre-fetcher results
            vs_uuid = self._find_target_vs_uuid(
                pre_fetch_results, 
                test_config['pre_validation']['target_vs_name']
            )
            
            if not vs_uuid:
                raise Exception(f"Target VS '{test_config['pre_validation']['target_vs_name']}' not found")
            
            # Stage 2: Pre-Validation
            logger.info("[STAGE 2: Pre-Validation]")
            pre_validation_result = self._execute_pre_validation(
                vs_uuid, 
                test_config['pre_validation']['expected_enabled']
            )
            result['stages']['pre_validation'] = pre_validation_result
            
            if not pre_validation_result['success']:
                raise Exception(f"Pre-validation failed: {pre_validation_result['message']}")
            
            # Execute mock actions
            logger.info("[MOCK ACTIONS]")
            mock_results = self._execute_mock_actions(test_config.get('mock_actions', []))
            result['stages']['mock_actions'] = mock_results
            
            # Stage 3: Task/Trigger
            logger.info("[STAGE 3: Task / Trigger]")
            task_result = self._execute_task_trigger(
                vs_uuid, 
                test_config['task_trigger']
            )
            result['stages']['task_trigger'] = task_result
            
            if not task_result['success']:
                raise Exception(f"Task trigger failed: {task_result['message']}")
            
            # Stage 4: Post-Validation
            logger.info("[STAGE 4: Post-Validation]")
            post_validation_result = self._execute_post_validation(
                vs_uuid,
                test_config['post_validation']['expected_enabled']
            )
            result['stages']['post_validation'] = post_validation_result
            
            if not post_validation_result['success']:
                raise Exception(f"Post-validation failed: {post_validation_result['message']}")
            
            logger.info(f"Test Case '{test_config['name']}' completed successfully")
            
        except Exception as e:
            logger.error(f"Test Case '{test_config['name']}' failed: {str(e)}")
            result['success'] = False
            result['error'] = str(e)
        
        self.test_results.append(result)
        return result
    
    def _execute_pre_fetcher(self, pre_fetcher_config):
        """Execute pre-fetcher stage"""
        results = {}
        
        for fetch_config in pre_fetcher_config:
            endpoint = fetch_config['endpoint']
            action = fetch_config['action']
            log_message = fetch_config['log_message']
            
            logger.info(f"Fetching {endpoint}...")
            response = self.api_client.make_request(action.upper(), endpoint)
            
            if response['success']:
                data = response['data']
                # Handle the API response structure
                if isinstance(data, dict) and 'results' in data:
                    count = len(data['results'])
                elif isinstance(data, list):
                    count = len(data)
                elif isinstance(data, dict):
                    count = 1
                else:
                    count = 1
                    
                logger.info(f"{log_message} | Count: {count}")
                results[endpoint] = {
                    'success': True,
                    'count': count,
                    'data': data
                }
            else:
                logger.error(f"Failed to fetch {endpoint}: {response['error']}")
                results[endpoint] = {
                    'success': False,
                    'error': response['error']
                }
        
        return results
    
    def _find_target_vs_uuid(self, pre_fetch_results, target_vs_name):
        """Find target virtual service UUID from pre-fetcher results"""
        vs_endpoint = '/api/virtualservice'
        if vs_endpoint in pre_fetch_results and pre_fetch_results[vs_endpoint]['success']:
            vs_data = pre_fetch_results[vs_endpoint]['data']
            
            # The API returns data in a 'results' array within a dict
            if isinstance(vs_data, dict) and 'results' in vs_data:
                # First, try to find the exact target name
                for vs in vs_data['results']:
                    if vs.get('name') == target_vs_name:
                        logger.info(f"SUCCESS: Found Virtual Service '{target_vs_name}' with UUID: {vs.get('uuid')}")
                        return vs.get('uuid')
                
                # If exact name not found, use the first available Virtual Service
                if vs_data['results']:
                    first_vs = vs_data['results'][0]
                    actual_name = first_vs.get('name', 'Unknown')
                    actual_uuid = first_vs.get('uuid')
                    if actual_uuid:
                        logger.warning(f"Target VS '{target_vs_name}' not found. Using first available: '{actual_name}'")
                        return actual_uuid
            
            # Also handle direct list response (backward compatibility)
            elif isinstance(vs_data, list):
                for vs in vs_data:
                    if isinstance(vs, dict) and vs.get('name') == target_vs_name:
                        logger.info(f"SUCCESS: Found Virtual Service '{target_vs_name}' with UUID: {vs.get('uuid')}")
                        return vs.get('uuid')
            
            logger.error(f"Could not find any suitable Virtual Service")
            return None
        
        logger.error(f"Failed to get Virtual Services data")
        return None
    
    def _execute_pre_validation(self, vs_uuid, expected_enabled):
        """Execute pre-validation stage"""
        logger.info(f"Validating Virtual Service with UUID '{vs_uuid}'...")
        response = self.api_client.get_virtual_service_by_uuid(vs_uuid)
        
        if not response['success']:
            return {
                'success': False,
                'message': f"Failed to get VS: {response['error']}"
            }
        
        vs_data = response['data']
        
        # Extract enabled state from the response
        if isinstance(vs_data, dict):
            actual_state = vs_data.get('enabled')
            vs_name = vs_data.get('name', 'Unknown')
        else:
            # Handle unexpected response format
            logger.error(f"Unexpected VS data format: {type(vs_data)}")
            return {
                'success': False,
                'message': f"Unexpected VS data format: {type(vs_data)}"
            }
        
        logger.info(f"Virtual Service '{vs_name}' current state: enabled={actual_state}")
        
        if actual_state == expected_enabled:
            message = f"Virtual Service '{vs_name}' is {'enabled' if expected_enabled else 'disabled'} as expected"
            logger.info(f"SUCCESS: Pre-validation passed. {message}")
            return {
                'success': True,
                'message': message,
                'vs_data': vs_data
            }
        else:
            message = f"Expected enabled={expected_enabled} but got enabled={actual_state}"
            logger.error(f"FAILED: Pre-validation failed. {message}")
            return {
                'success': False,
                'message': message,
                'vs_data': vs_data
            }
    
    def _execute_mock_actions(self, mock_actions):
        """Execute mock SSH/RDP actions"""
        results = []
        
        for action in mock_actions:
            if action['type'] == 'ssh':
                logger.info(f"MOCK_SSH: Connecting to host...")
                logger.info(f"MOCK_SSH: Executing command '{action['command']}'...")
                logger.info(f"MOCK_SSH: Command executed successfully")
                results.append({'type': 'ssh', 'success': True})
            elif action['type'] == 'rdp':
                logger.info(f"MOCK_RDP: Validating remote connection to {action['target']}...")
                logger.info(f"MOCK_RDP: Connection established successfully")
                results.append({'type': 'rdp', 'success': True})
        
        return results
    
    def _execute_task_trigger(self, vs_uuid, task_config):
        """Execute task/trigger stage"""
        endpoint = task_config['endpoint'].format(vs_uuid=vs_uuid)
        payload = task_config['payload']
        
        logger.info(f"Sending {task_config['action'].upper()} request to update Virtual Service...")
        response = self.api_client.make_request(task_config['action'].upper(), endpoint, payload)
        
        if response['success']:
            logger.info("SUCCESS: Virtual Service update request sent successfully")
            return {
                'success': True,
                'message': "Virtual Service update request sent successfully",
                'response_data': response['data']
            }
        else:
            logger.error(f"FAILED: Failed to update VS: {response['error']}")
            return {
                'success': False,
                'message': f"Failed to update VS: {response['error']}"
            }
    
    def _execute_post_validation(self, vs_uuid, expected_enabled):
        """Execute post-validation stage"""
        logger.info("Sending GET request to verify Virtual Service status...")
        response = self.api_client.get_virtual_service_by_uuid(vs_uuid)
        
        if not response['success']:
            return {
                'success': False,
                'message': f"Failed to get VS for post-validation: {response['error']}"
            }
        
        vs_data = response['data']
        
        # Extract enabled state from the response
        if isinstance(vs_data, dict):
            actual_state = vs_data.get('enabled')
            vs_name = vs_data.get('name', 'Unknown')
        else:
            # Handle unexpected response format
            logger.error(f"Unexpected VS data format: {type(vs_data)}")
            return {
                'success': False,
                'message': f"Unexpected VS data format: {type(vs_data)}"
            }
        
        logger.info(f"Virtual Service '{vs_name}' new state: enabled={actual_state}")
        
        if actual_state == expected_enabled:
            message = f"Virtual Service '{vs_name}' is {'enabled' if expected_enabled else 'disabled'} as expected"
            logger.info(f"SUCCESS: Post-validation passed. {message}")
            return {
                'success': True,
                'message': message,
                'vs_data': vs_data
            }
        else:
            message = f"Expected enabled={expected_enabled} but got enabled={actual_state}"
            logger.error(f"FAILED: Post-validation failed. {message}")
            return {
                'success': False,
                'message': message,
                'vs_data': vs_data
            }
    
    def run_tests_parallel(self, test_configs, max_workers=2):
        """Run multiple test cases in parallel"""
        logger.info(f"--- Starting Parallel Test Execution with {max_workers} workers ---")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_test = {
                executor.submit(self.execute_test_case, config): config 
                for config in test_configs
            }
            
            for future in concurrent.futures.as_completed(future_to_test):
                test_config = future_to_test[future]
                try:
                    result = future.result()
                    logger.info(f"Completed: {test_config['name']} - Success: {result['success']}")
                except Exception as e:
                    logger.error(f"Test {test_config['name']} generated exception: {str(e)}")
        
        logger.info("--- Parallel Execution Finished ---")
        return self.test_results