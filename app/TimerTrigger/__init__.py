import datetime
import logging
from shared import settings

import azure.core as core
import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.containerinstance import ContainerInstanceManagementClient


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('The timer trigger function ran at %s', utc_timestamp)

    credential = DefaultAzureCredential()

    resource_client = ResourceManagementClient(
        credential, settings.SUBSCRIPTION_ID
    )

    # Check for the existence of resource group
    logging.info('Checking resource group.')
    try:
        resource_group = resource_client.resource_groups.get(
            settings.RESOURCE_GROUP_NAME
        )
    except core.exceptions.HttpResponseError as e:
        if e.status_code == 404:
            logging.exception(
                'Not found Resource Group: %s.',
                settings.RESOURCE_GROUP_NAME
            )
            raise
        else:
            logging.exception(
                'Got exception in resource group check: %s',
                e.status_code
            )
            raise

    aci_client = ContainerInstanceManagementClient(
        credential, settings.SUBSCRIPTION_ID
    )

    # Check for the existence of container group
    logging.info('Checking container group.')
    try:
        container_group = aci_client.container_groups.get(
            resource_group.name, settings.CONTAINER_GROUP_NAME
        )
        if container_group.instance_view.state == 'Succeeded':
            logging.info(
                'Found container group: %s. Cleaning up...',
                container_group.name
            )
            poller = aci_client.container_groups.begin_delete(
                resource_group.name, container_group.name
            )
            logging.info(
                'Cleaned up %s.',
                poller.result().name
            )
        else:
            logging.exception(
                'Container group: %s did not exit successfully the last time.',
                settings.CONTAINER_GROUP_NAME
            )
            raise
    except core.exceptions.HttpResponseError as e:
        if e.status_code == 404:
            logging.info(
                'Not found container group: %s.',
                settings.CONTAINER_GROUP_NAME
            )
        else:
            logging.exception(
                'Got exception in existing container group check: % s',
                e.status_code
            )
            raise

    # Create container group
    logging.info('Creating container group.')
    try:
        poller = aci_client.container_groups.begin_create_or_update(
            resource_group.name,
            settings.CONTAINER_GROUP_NAME,
            settings.CONTAINER_GROUP
        )
        logging.info(
            'Created container group %s.',
            poller.result().name
        )
    except core.exceptions.HttpResponseError as e:
        logging.exception(
            'Got exception in creating container group: %s',
            e.status_code
        )
        raise
