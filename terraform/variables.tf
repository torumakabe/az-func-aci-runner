variable "aci_runner_rg" {
  type = string
}

variable "aci_runner_location" {
  type = string
}

variable "prefix" {
  type = string
  validation {
    condition     = length(var.prefix) <= 14
    error_message = "The prefix value must be 14 characters or less."
  }
}

variable "appinsights_ikey" {
  type      = string
  default   = null
  sensitive = true
}

variable "log_analytics" {
  type = object({
    workspace_id  = string
    workspace_key = string
  })
  sensitive = true
}

variable "github_token" {
  type      = string
  sensitive = true
}

variable "github_repo" {
  type = string
}

variable "azure_credentials" {
  type = object({
    subscription_id = string
    tenant_id       = string
    client_id       = string
    client_secret   = string
  })
  sensitive = true
}
