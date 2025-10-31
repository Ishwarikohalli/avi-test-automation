import requests
import json
import logging

class AviApiClient:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.token = None
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
    
    def register(self):
        """Register with AVI API"""
        try:
            register_url = f"{self.base_url}/register"
            payload = {
                "username": self.username,
                "password": self.password
            }
            response = self.session.post(register_url, json=payload)
            
            if response.status_code in [200, 201]:
                self.logger.info("Successfully registered")
                return True
            else:
                self.logger.warning(f"Registration response: {response.status_code} - {response.text}")
                return True
        except Exception as e:
            self.logger.error(f"Registration error: {str(e)}")
            return False
    
    def login(self):
        """Login to AVI API and get bearer token"""
        try:
            self.register()
            
            login_url = f"{self.base_url}/login"
            response = self.session.post(
                login_url,
                auth=(self.username, self.password)
            )
            
            if response.status_code == 200:
                # Try to parse as JSON first, then as text
                try:
                    response_data = response.json()
                    self.token = response_data.get('token')
                except:
                    # If JSON parsing fails, try to extract token from text
                    self.token = response.text.strip()
                
                if self.token:
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.token}',
                        'Content-Type': 'application/json'
                    })
                    self.logger.info("Successfully logged in and obtained token")
                    return True
                else:
                    self.logger.error("No token received in login response")
                    return False
            else:
                self.logger.error(f"Login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Login error: {str(e)}")
            return False
    
    def make_request(self, method, endpoint, payload=None):
        """Make API request to AVI"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=payload)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=payload)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            self.logger.debug(f"API {method} {endpoint} -> Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                # Try to parse as JSON, if fails return as text
                try:
                    response_data = response.json()
                    return {
                        'success': True,
                        'data': response_data,
                        'status_code': response.status_code,
                        'is_json': True
                    }
                except json.JSONDecodeError:
                    # If it's not JSON, return as text
                    return {
                        'success': True,
                        'data': response.text,
                        'status_code': response.status_code,
                        'is_json': False
                    }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}",
                    'status_code': response.status_code
                }
                
        except Exception as e:
            self.logger.error(f"API request failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_all_virtual_services(self):
        return self.make_request('GET', '/api/virtualservice')
    
    def get_virtual_service_by_uuid(self, uuid):
        return self.make_request('GET', f'/api/virtualservice/{uuid}')
    
    def update_virtual_service(self, uuid, payload):
        return self.make_request('PUT', f'/api/virtualservice/{uuid}', payload)
    
    def get_all_tenants(self):
        return self.make_request('GET', '/api/tenant')
    
    def get_all_service_engines(self):
        return self.make_request('GET', '/api/serviceengine')