# ACI Runner on Azure Functions

## Table of Contents

- [About](#about)
- [Getting Started](#getting_started)

## About <a name = "about"></a>

Azure Container Instances Runner on Azure Functions. A timmer trigger function written in Python.

<img src="https://raw.githubusercontent.com/ToruMakabe/Images/master/aci-runner.png?raw=true" width="800">

## Getting Started <a name = "getting_started"></a>

First, build the platform with Terraform. Then deploy the function in GitHub Actions. Pushing tags with semantic versioning (vx.y.z) will run the deployment workflow.

### Prerequisites & Tested

* Terraform: 1.0.1
  * hashicorp/azurerm: 2.66
  * integrations/github: 4.12
* Azure Functions
  * Plan: Consumption
  * OS: Linux
  * Runtime: Python 3.8

### Notes

#### Config options and the evaluation order

Each params takes precedence over the item below it. For example, setting an env. var overrides the same parameter in the configuration file.

* Key Vault secret ([settings.py](https://github.com/ToruMakabe/az-func-aci-runner/blob/main/app/shared/settings.py))
* env. var
* config file ([settings.ini](https://github.com/ToruMakabe/az-func-aci-runner/blob/main/app/shared/settings.ini))
* default in code ([settings.py](https://github.com/ToruMakabe/az-func-aci-runner/blob/main/app/shared/settings.py))
