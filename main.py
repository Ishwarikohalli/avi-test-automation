#!/usr/bin/env python3

import os
import sys
import logging
import yaml

# Add the test-framework directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'test-framework'))

from api_client import AviApiClient
from test_runner import TestRunner

def load_yaml_config(file_path):
    """Load YAML configuration file"""
    try:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        logging.error(f"Error loading YAML file {file_path}: {str(e)}")
        return None

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def main():
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Avi Test Framework...")
    
    # Load configuration
    config = load_yaml_config('config.yaml')
    if not config:
        logger.error("Failed to load config.yaml")
        sys.exit(1)
    
    # Initialize API client and login
    api_config = config['api']
    api_client = AviApiClient(
        api_config['base_url'],
        api_config['username'],
        api_config['password']
    )
    
    if not api_client.login():
        logger.error("Failed to login to AVI API")
        sys.exit(1)
    
    # DEBUG: Check what virtual services actually exist
    logger.info("=== Checking available Virtual Services ===")
    response = api_client.get_all_virtual_services()
    if response['success']:
        vs_data = response['data']
        if isinstance(vs_data, dict) and 'results' in vs_data:
            logger.info(f"Found {len(vs_data['results'])} Virtual Services:")
            for vs in vs_data['results']:
                vs_name = vs.get('name', 'Unknown')
                vs_uuid = vs.get('uuid', 'Unknown')
                vs_enabled = vs.get('enabled', 'Unknown')
                logger.info(f"  - Name: {vs_name}")
                logger.info(f"    UUID: {vs_uuid}")
                logger.info(f"    Enabled: {vs_enabled}")
                logger.info("    ---")
        else:
            logger.warning("Unexpected Virtual Services data structure")
            logger.info(f"Response keys: {list(vs_data.keys()) if isinstance(vs_data, dict) else 'Not a dict'}")
    else:
        logger.error(f"Failed to get Virtual Services: {response['error']}")
    
    # Load test cases
    test_configs = []
    for test_case_path in config['test_cases']:
        test_config = load_yaml_config(test_case_path)
        if test_config:
            test_configs.append(test_config)
        else:
            logger.error(f"Failed to load test case: {test_case_path}")
    
    if not test_configs:
        logger.error("No valid test cases found")
        sys.exit(1)
    
    # Initialize test runner and execute tests
    test_runner = TestRunner(api_client)
    
    if config['parallel_execution']['enabled']:
        # Run tests in parallel
        test_runner.run_tests_parallel(
            test_configs, 
            config['parallel_execution']['max_workers']
        )
    else:
        # Run tests sequentially
        for test_config in test_configs:
            test_runner.execute_test_case(test_config)
    
    # Print summary
    successful_tests = sum(1 for result in test_runner.test_results if result['success'])
    total_tests = len(test_runner.test_results)
    
    logger.info(f"=== TEST SUMMARY ===")
    logger.info(f"Successful: {successful_tests}/{total_tests}")
    logger.info(f"Failed: {total_tests - successful_tests}/{total_tests}")

if __name__ == "__main__":
    main()