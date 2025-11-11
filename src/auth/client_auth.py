import logging, os
from azure.identity import DefaultAzureCredential, OnBehalfOfCredential, get_bearer_token_provider

# Use the main logger for the application
logger = logging.getLogger(__name__)

# Obtain Entra ID access token using the OAuth client credentials flow
def get_access_token_client_credentials(scope):
    try: 
        logger.info("Obtaining access token using client credentials flow")
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(),
            scope
        )
        logger.info("Access token obtained successfully for client credentials flow")
        return token_provider
    except:
        logger.error('Failed to obtain access token for client credentials flow: ', exc_info=True)

def get_access_token_on_behalf_of(scope, user_assertion):
    try:
        logger.info("Obtaining access token using on-behalf-of flow")
        credential = OnBehalfOfCredential(
            client_id=os.getenv("AZURE_CLIENT_ID"),
            client_secret=os.getenv("AZURE_CLIENT_SECRET"),
            tenant_id=os.getenv("AZURE_TENANT_ID"),
            user_assertion=user_assertion
        )
        
        token_provider = get_bearer_token_provider(
            credential,
            scope
        )
        
        logger.info("Access token obtained successfully for on-behalf-of flow")
        return token_provider
    except:
        logger.error('Failed to obtain access token for on-behalf-of flow: ', exc_info=True)