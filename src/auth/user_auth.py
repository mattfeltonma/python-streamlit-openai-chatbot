import msal
import logging
import streamlit as st
from typing import Optional, Dict

# Use the main logger for the application
logger = logging.getLogger(__name__)

# Define a new class to represent a logged in Entra ID user
class EntraUserAuth:

    MS_GRAPH_SCOPES = ["User.Read"]

    def __init__(self, client_id: str, tenant_id: str, redirect_uri: str, client_secret: str):
        self.client_id = client_id
        self.tenant_id = tenant_id
        self.authority = f"https://login.microsoftonline.com/{tenant_id}"
        self.redirect_uri = redirect_uri
        
        # Configure as OAuth confidential client
        self.app = msal.ConfidentialClientApplication(
            client_id=client_id,
            client_credential=client_secret,
            authority=self.authority,
        )
    
    # Function that generates a login URL with the MS Graph API scopes the application is requesting the user's consent for
    def get_login_url(self) -> str:
        """Generate login URL for Entra ID authentication."""
        auth_url = self.app.get_authorization_request_url(
            scopes=self.MS_GRAPH_SCOPES,
            redirect_uri=self.redirect_uri
        )
        return auth_url
    
    # Function that acquires the Entra ID issued access token for the MS Graph API using the OAuth authorization code flow
    def handle_callback(self, auth_code: str) -> Optional[Dict]:
        """Handle the callback from Entra ID with auth code."""
        try:
            result = self.app.acquire_token_by_authorization_code(
                auth_code,
                scopes=self.MS_GRAPH_SCOPES,
                redirect_uri=self.redirect_uri
            )
            
            # If an access token is returned, store it in the access token variable, make a call to the Microsoft Graph
            # API to retieve additional user attributes, and set the expires_in variable
            if "access_token" in result:
                return {
                    "access_token": result["access_token"],
                    "id_token": result.get("id_token"), 
                    "user_info": self._get_user_info(result["access_token"]),
                    "expires_in": result.get("expires_in")
                }
        
        except Exception as e:
            st.error(f"Authentication failed and unable to obtain access token for Microsoft Graph API: {e}")
        
        return None
    
    # Function that retrieves an Entra ID issued access token for this application
    def get_application_token(self) -> Optional[Dict]:
        """Get application access token for the application itself."""
        try:

            # Get the cached account from a prior login
            accounts = self.app.get_accounts()
            if not accounts:
                logger.error("No cached accounts found for silent token acquisition")
                return None

            account = accounts[0]

            result = self.app.acquire_token_silent(
                scopes=[f"api://{self.client_id}/user_impersonation"],
                account=account
            )

            logging.info(f"This is the result: {result}")
            
            # If an access token is returned, store it in the access token variable, and set the expires_in variable
            if "access_token" in result:
                return {
                    "access_token_app": result["access_token"],
                    "expires_in_app": result.get("expires_in")
                }
            
        except Exception as e:
            st.error(f"Authentication failed and unable to obtain application access token: {e}")
        
        return None

    # Use the access token the application has obtained to query the MS Graph for additional user attributes
    def _get_user_info(self, access_token: str) -> Dict:
        """Get additional user attributes for the user from the Microsoft Graph API"""
        import requests
        
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(
            "https://graph.microsoft.com/v1.0/me",
            headers=headers
        )
        
        if response.status_code == 200:
            user_data = response.json()
            
            # Log the user attributes returned by the Microsoft Graph API
            logger.info(f"Microsoft Graph user properties: {list(user_data.keys())}")
            return user_data
        return {}