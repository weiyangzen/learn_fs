# sources/test-tools/kdevops/terraform/azure/scripts/gen_kconfig_location

## Purpose
This script discovers Azure regions and renders Azure location Kconfig choices or raw region details.

## Important APIs, Types, And Functions
`get_region_friendly_name()` combines display name and physical location when available. `get_region_info()` finds one region in an already fetched region list. `output_region_kconfig()` prints one `config TERRAFORM_AZURE_REGION_<NAME>` stanza and optional paired-region help. `output_regions_kconfig()` renders all regions via `regions.j2` after adding friendly names. Raw output functions print region tables and metadata. `parse_arguments()` supports optional region name, `--regions`, `--format`, and `--quiet`.

## Control Flow
`main()` validates credentials with optional skip-on-absent behavior, fetches regions, then either lists all regions, emits one region, or renders the complete regions Kconfig. The default region is converted to a Kconfig-safe symbol for template defaults.

## State And Persistence
The script writes stdout only. It reads Azure authentication/config state through `azure_common.py` and live subscription location metadata. No cache is maintained.

## Dependencies And Integration Points
It depends on `azure_common.py`, Azure SDK region discovery, and the `regions.j2` template. Generated content is sourced by `terraform/azure/Kconfig`.

## Risks And Test Signals
Account/subscription permissions can affect visible locations. The raw output assumes `displayName` is present. Kconfig output is only as good as the template and naming conversion. Tests should mock region lists with physical and paired metadata, missing metadata, unknown region lookup, no-credential skip behavior, and template rendering.
