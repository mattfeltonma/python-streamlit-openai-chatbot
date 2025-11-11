"""
User security context class which is used to pass user identity information for Defender for Cloud's Defender for AI and Purview capability
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any

@dataclass
class UserSecurityContext:
    """Security context of the logged in user"""

    application_name: str
    end_user_id: str
    source_ip: str
    end_user_tenant_id: Optional[str] = None

    # Convert this to a dictionary in the format expected by Azure OpenAI
    def to_dict(self) -> Dict[str, Any]:
        # Return the raw fields for use in extra_body
        return {
            "application_name": self.application_name,
            "end_user_id": self.end_user_id,
            "source_ip": self.source_ip,
            "end_user_tenant_id": self.end_user_tenant_id
        }
    

def get_msdefender_user_json(authenticated_user_details, application_name, tenant_id=None, source_ip=None) -> UserSecurityContext:
    """
    Create security context for Microsoft Defender for AI and Purview integration.
    Source: https://github.com/microsoft/sample-app-aoai-chatGPT/blob/main/backend/security/ms_defender_utils.py
    Args:
        authenticated_user_details: Entra ID User information pulled from Microsoft Graph API
        application_name: Name of the application the user logged into
        tenant_id: The user's source Entra ID tenant
        source_ip: The user's endpoint IP address
    """
    
    # If source_ip cannot be specified, such as instance of running Streamlit locally, then pass unknown
    if source_ip is None:
        source_ip = 'unknown'
    
    # If IP includes a port clean it up and pass just the IP address
    if ':' in source_ip:
        source_ip = source_ip.split(':')[0]

    # From the returned Microsoft Graph API user object, get the user's Entra ID object ID and 
    end_user_id = authenticated_user_details.get('id')

    # Tenant ID is not stored in Microsoft Graph API user object so it must be set separately
    end_user_tenant_id = tenant_id

    # Return the UserSecurityContext object
    return UserSecurityContext(
        end_user_id=end_user_id, 
        source_ip=source_ip, 
        application_name=application_name, 
        end_user_tenant_id=end_user_tenant_id
    )