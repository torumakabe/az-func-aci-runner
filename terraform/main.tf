terraform {
  required_version = "~> 1.0.1"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 2.66"
    }

    github = {
      source  = "integrations/github"
      version = "~> 4.12"
    }

  }
}

provider "azurerm" {
  features {}
}

data "azurerm_client_config" "current" {
}

resource "azurerm_resource_group" "aci_runner" {
  name     = var.aci_runner_rg
  location = var.aci_runner_location
}

resource "azurerm_storage_account" "aci_runner" {
  name                     = "${var.prefix}stacirunner"
  resource_group_name      = azurerm_resource_group.aci_runner.name
  location                 = azurerm_resource_group.aci_runner.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_app_service_plan" "aci_runner" {
  name                = "plan-aci-runner"
  location            = azurerm_resource_group.aci_runner.location
  resource_group_name = azurerm_resource_group.aci_runner.name
  kind                = "FunctionApp"
  reserved            = true

  sku {
    tier = "Dynamic"
    size = "Y1"
  }
}

resource "azurerm_function_app" "aci_runner" {
  name                       = "${var.prefix}-func-aci-runner"
  location                   = azurerm_resource_group.aci_runner.location
  resource_group_name        = azurerm_resource_group.aci_runner.name
  app_service_plan_id        = azurerm_app_service_plan.aci_runner.id
  storage_account_name       = azurerm_storage_account.aci_runner.name
  storage_account_access_key = azurerm_storage_account.aci_runner.primary_access_key
  os_type                    = "linux"
  version                    = "~3"
  identity {
    type = "SystemAssigned"
  }

  site_config {
    linux_fx_version = "PYTHON|3.8"
  }

  app_settings = {
    "FUNCTIONS_WORKER_RUNTIME"       = "python"
    "APPINSIGHTS_INSTRUMENTATIONKEY" = var.appinsights_ikey
    "ACI_SUBSCRIPTION_ID"            = data.azurerm_client_config.current.subscription_id
    "ACI_RESOURCE_GROUP_NAME"        = azurerm_resource_group.aci_runner.name
    "ACI_CONTAINER_GROUP_NAME"       = local.container_group_name
    "ACI_CONTAINER_GROUP_LOCATION"   = azurerm_resource_group.aci_runner.location
    "KEY_VAULT_NAME"                 = local.wordcount_app_kv_name
  }

  lifecycle {
    ignore_changes = [
      app_settings["WEBSITE_ENABLE_SYNC_UPDATE_SITE"],
      app_settings["WEBSITE_RUN_FROM_PACKAGE"]
    ]
  }
}

resource "azurerm_role_assignment" "mi_aci_runnner_rg_contributor" {
  scope                = azurerm_resource_group.aci_runner.id
  role_definition_name = "Contributor"
  principal_id         = azurerm_function_app.aci_runner.identity[0].principal_id
}

resource "azurerm_key_vault" "wordcount_app" {
  name                = local.wordcount_app_kv_name
  location            = azurerm_resource_group.aci_runner.location
  resource_group_name = azurerm_resource_group.aci_runner.name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "standard"

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id

    secret_permissions = [
      "backup",
      "delete",
      "get",
      "list",
      "purge",
      "recover",
      "restore",
      "set",
    ]
  }

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = azurerm_function_app.aci_runner.identity[0].principal_id

    secret_permissions = [
      "get",
      "list",
    ]
  }
}

resource "azurerm_key_vault_secret" "la_ws_id" {
  name         = "la-ws-id"
  value        = var.log_analytics.workspace_id
  key_vault_id = azurerm_key_vault.wordcount_app.id
}

resource "azurerm_key_vault_secret" "la_ws_key" {
  name         = "la-ws-key"
  value        = var.log_analytics.workspace_key
  key_vault_id = azurerm_key_vault.wordcount_app.id
}

provider "github" {
  token = var.github_token
}

data "github_actions_public_key" "az_func_aci_runner" {
  repository = var.github_repo
}

resource "github_actions_secret" "azure_credentials_subscription_id" {
  repository      = var.github_repo
  secret_name     = "AZURE_SUBSCRIPTION_ID"
  plaintext_value = var.azure_credentials.subscription_id
}

resource "github_actions_secret" "azure_credentials_tenant_id" {
  repository      = var.github_repo
  secret_name     = "AZURE_TENANT_ID"
  plaintext_value = var.azure_credentials.tenant_id
}

resource "github_actions_secret" "azure_credentials_client_id" {
  repository      = var.github_repo
  secret_name     = "AZURE_CLIENT_ID"
  plaintext_value = var.azure_credentials.client_id
}

resource "github_actions_secret" "azure_credentials_client_secret" {
  repository      = var.github_repo
  secret_name     = "AZURE_CLIENT_SECRET"
  plaintext_value = var.azure_credentials.client_secret
}

resource "github_actions_secret" "azure_credentials_app_name" {
  repository      = var.github_repo
  secret_name     = "AZURE_FUNCTIONAPP_NAME"
  plaintext_value = azurerm_function_app.aci_runner.name
}
