# sources/test-tools/kdevops/terraform/azure/scripts/publisher_definitions.yml

## Purpose
This YAML file is the policy/configuration source for Azure image publishers supported by `gen_kconfig_image`. It records Azure publisher IDs, display names, descriptions, priorities, and optional offer regex filters.

## Important APIs, Types, And Functions
Top-level keys are publisher identifiers such as `debian`, `redhat`, `canonical`, `oracle`, `suse`, `almalinux`, and `rockylinux`. Required fields are `publisher_id`, `publisher_name`, `description`, and `priority`. Some entries include `offer_patterns`, which are regex strings matched against Azure offer names before SKU classification.

## Control Flow
There is no executable flow. `gen_kconfig_image` loads this file with PyYAML, sorts publishers by priority, queries each `publisher_id`, and applies `offer_patterns` to filter relevant offers.

## State And Persistence
The file persists curated publisher metadata in the repository. It does not include secrets. Updating it changes future generated Azure image Kconfig output.

## Dependencies And Integration Points
It integrates directly with Azure image discovery and indirectly with menuconfig and Terraform image variables. Comments document using `az vm image list-publishers --location westus` to find publisher IDs.

## Risks And Test Signals
Marketplace publisher IDs for AlmaLinux and Rocky Linux are timestamp-like and may become stale. Regex filters can be too broad or too narrow, hiding useful images or including unsupported variants. Tests should load the YAML, validate required fields and priority uniqueness/order, compile all regexes, and run fixture offers through expected filters.
