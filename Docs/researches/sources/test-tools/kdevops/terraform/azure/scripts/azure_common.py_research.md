# sources/test-tools/kdevops/terraform/azure/scripts/azure_common.py

## Purpose
This module centralizes Azure SDK, authentication, region, VM-size, image-offer, Jinja, and error-handling helpers for Azure Kconfig generator scripts.

## Important APIs, Types, And Functions
`AzureNotConfiguredError` marks optional auth absence. `get_default_region()` uses Azure CLI profile validation, `AZURE_DEFAULTS_LOCATION`, `~/.azure/config`, and fallback `westus`. `get_all_regions()` uses `SubscriptionClient.list_locations()` and skips logical regions. `get_compute_client()` builds `ComputeManagementClient` from CLI credentials. `get_vm_sizes_and_skus()` queries resource SKUs once per region and derives size records plus capability dictionaries. `get_all_offers_and_skus()` lists image offers and fetches SKUs in parallel. `exit_on_empty_result()` exits with diagnostics. `require_azure_credentials()` validates CLI credentials and distinguishes auth-like failures from other exceptions.

## Control Flow
Generator scripts call `require_azure_credentials()` first when live Azure data is required. Region, size, and image helpers authenticate via Azure CLI profile, call SDK list operations, convert SDK objects to plain dictionaries, and return empty structures on query failures while printing optional diagnostics.

## State And Persistence
It reads Azure CLI auth/config state and environment variables but writes no files. Returned metadata is transient and consumed by renderers. Azure SDK token/session state is managed by the Azure libraries.

## Dependencies And Integration Points
It depends on `azure.common.credentials`, `azure.mgmt.resource`, `azure.mgmt.compute`, `jinja2`, and Python config/json/os modules. It is imported by Azure location, size, and image generators and shares templates from caller directories.

## Risks And Test Signals
The Azure SDK import path `azure.common.credentials` is from older Azure SDK conventions and may not be installed in newer environments. Broad exception handling can turn service failures into empty generated menus. SKU capability parsing assumes numeric capability names are present and parseable. Tests should mock CLI profiles and SDK clients, cover missing SDK/auth, region config precedence, SKU parsing failures, offer filtering, and generated structures for logical vs physical locations.
