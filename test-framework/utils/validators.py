import logging

logger = logging.getLogger(__name__)

def mock_ssh(command):
    """Mock SSH connection and command execution"""
    logger.info(f"MOCK_SSH: Connecting to host...")
    logger.info(f"MOCK_SSH: Executing command '{command}'...")
    logger.info(f"MOCK_SSH: Command executed successfully")
    return {"success": True, "output": f"Mock output for: {command}"}

def mock_rdp(target):
    """Mock RDP connection"""
    logger.info(f"MOCK_RDP: Validating remote connection to {target}...")
    logger.info(f"MOCK_RDP: Connection established successfully")
    return {"success": True, "connected_to": target}

def validate_virtual_service_state(vs_data, expected_enabled):
    """Validate virtual service enabled state"""
    if not vs_data or 'enabled' not in vs_data:
        return False, "Virtual service data or enabled field missing"
    
    actual_state = vs_data['enabled']
    if actual_state == expected_enabled:
        return True, f"Virtual Service is {'enabled' if expected_enabled else 'disabled'} as expected"
    else:
        return False, f"Expected enabled={expected_enabled} but got enabled={actual_state}"

def find_virtual_service_by_name(vs_list, target_name):
    """Find virtual service by name in list"""
    if not vs_list:
        return None
    
    for vs in vs_list:
        if vs.get('name') == target_name:
            return vs
    
    return None