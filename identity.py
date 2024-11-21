import logging
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Obtain Entra ID access token using service principal credentials
def get_access_token(scope,service_principal):
    try:
        if service_principal == "Service Principal 1":
            load_dotenv('.sp1_secret')
        elif service_principal == "Service Principal 2":
            load_dotenv('.sp2_secret')
    except:
        logging.error('Failed to load env variables: ', exc_info=True)

    try: 
        logging.info("Obtaining access token")
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(
                connection_verify=False
            ),
            scope
        )
        
        return token_provider
    except:
        logging.error('Failed to obtain access token: ', exc_info=True)