from decouple import config

import azure.core as core
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

# import models you need
# https://docs.microsoft.com/en-us/python/api/azure-mgmt-containerinstance/azure.mgmt.containerinstance.models?view=azure-python
from azure.mgmt.containerinstance.models import (
    ContainerGroup,
    Container,
    ResourceRequirements,
    ResourceRequests,
    OperatingSystemTypes,
    ContainerGroupDiagnostics,
    LogAnalytics,
    EnvironmentVariable
)

# values from settings.ini and you can override with env. variables
SUBSCRIPTION_ID = config('ACI_SUBSCRIPTION_ID')
RESOURCE_GROUP_NAME = config('ACI_RESOURCE_GROUP_NAME')
CONTAINER_GROUP_NAME = config('ACI_CONTAINER_GROUP_NAME')
CONTAINER_GROUP_LOCATION = config('ACI_CONTAINER_GROUP_LOCATION')
CONTAINER_GROUP_RESTART_POLICY = config(
    'ACI_CONTAINER_GROUP_RESTART_POLICY',
    default='Never'
)
CONTAINER_NAME = config('ACI_CONTAINER_NAME')
CONTAINER_IMAGE = config('ACI_CONTAINER_IMAGE')
CONTAINER_RESOURCE_REQUEST_CPU = config(
    'ACI_CONTAINER_RESOURCE_REQUEST_CPU',
    default=1.0
)
CONTAINER_RESOURCE_REQUEST_MEM_GB = config(
    'ACI_CONTAINER_RESOURCE_REQUEST_MEM_GB',
    default=1.0
)
CONTAINER_ENVVAR_NUMWORDS = config(
    'ACI_CONTAINER_ENVVAR_NUMWORDS', default='10')
CONTAINER_ENVVAR_MINLENGTH = config(
    'ACI_CONTAINER_ENVVAR_MINLENGTH', default='1')
LOG_ANALYTICS_WS_ID = config('ACI_LOG_ANALYTICS_WS_ID', default='')
LOG_ANALYTICS_WS_KEY = config('ACI_LOG_ANALYTICS_WS_KEY', default='')

KEY_VAULT_NAME = config('KEY_VAULT_NAME', default='')

# override when using key vault
if KEY_VAULT_NAME != '':
    kv_url = f"https://{KEY_VAULT_NAME}.vault.azure.net"
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=kv_url, credential=credential)

    try:
        secret_id = client.get_secret("la-ws-id")
        LOG_ANALYTICS_WS_ID = secret_id.value
        secret_key = client.get_secret("la-ws-key")
        LOG_ANALYTICS_WS_KEY = secret_key.value
    except core.exceptions.HttpResponseError:
        raise

# add & modify params you need
container_resource_requests = ResourceRequests(
    memory_in_gb=CONTAINER_RESOURCE_REQUEST_MEM_GB,
    cpu=CONTAINER_RESOURCE_REQUEST_CPU
)
container_resource_requirements = ResourceRequirements(
    requests=container_resource_requests
)
container_env_vars = [
    EnvironmentVariable(
        name='NumWords',
        secure_value=CONTAINER_ENVVAR_NUMWORDS
    ),
    EnvironmentVariable(
        name='MinLength',
        secure_value=CONTAINER_ENVVAR_MINLENGTH
    ),
]
container = Container(
    name=CONTAINER_NAME,
    image=CONTAINER_IMAGE,
    resources=container_resource_requirements,
    environment_variables=container_env_vars
)

# if you want to create multi containers,
# make additional containers definition as above

if (LOG_ANALYTICS_WS_ID != '') and (LOG_ANALYTICS_WS_KEY != ''):
    log_analytics_settings = LogAnalytics(
        workspace_id=LOG_ANALYTICS_WS_ID,
        workspace_key=LOG_ANALYTICS_WS_KEY
    )
    diagnostics_settings = ContainerGroupDiagnostics(
        log_analytics=log_analytics_settings
    )
    CONTAINER_GROUP = ContainerGroup(
        containers=[container],
        location=CONTAINER_GROUP_LOCATION,
        os_type=OperatingSystemTypes.linux,
        restart_policy=CONTAINER_GROUP_RESTART_POLICY,
        diagnostics=diagnostics_settings
    )
else:
    CONTAINER_GROUP = ContainerGroup(
        containers=[container],
        location=CONTAINER_GROUP_LOCATION,
        restart_policy=CONTAINER_GROUP_RESTART_POLICY,
        os_type=OperatingSystemTypes.linux
    )
