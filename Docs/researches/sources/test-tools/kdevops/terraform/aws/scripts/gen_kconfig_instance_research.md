# sources/test-tools/kdevops/terraform/aws/scripts/gen_kconfig_instance

## Purpose
This script queries AWS EC2 instance-type metadata and renders Kconfig menus or raw tables for EC2 instance families and specific instance types.

## Important APIs, Types, And Functions
`parse_all_instance_families()` groups `describe_instance_types` records by prefix before the dot and tracks counts, GPU presence, and architectures. `get_gpu_info()` formats GPU names/counts/memory from `GpuInfo`. `get_instance_family_info()` filters instances in a family and extracts vCPUs, memory, CPU ISA, GPU, network performance, storage, bare-metal, free-tier, and placeholder pricing. Output functions render Jinja templates `families.j2` and `family.j2` or raw tables. `parse_arguments()` supports family selection, `--families`, `--format`, `--quiet`, and `--region`.

## Control Flow
`main()` validates AWS credentials but exits 0 if absent so dynamic config can be optional. It chooses region, fetches all instance types once, then either lists families, renders one family, or renders all families and their instance choices. Kconfig full output first prints the family selector then one section per family.

## State And Persistence
The script writes only stdout. AWS instance metadata is live remote state. In-memory state is the instance-type list and derived family dictionaries.

## Dependencies And Integration Points
It imports shared helpers from `aws_common.py`, depends on boto3 EC2 `describe_instance_types`, and renders Jinja templates from the script directory. It feeds generated AWS compute Kconfig fragments consumed by `terraform/aws/Kconfig`.

## Risks And Test Signals
Family parsing assumes the dot-delimited EC2 naming convention. Pricing is always "Not available", so raw output can look more complete than it is. Architecture and GPU detection depend on fields present in AWS responses. Tests should mock instance-type pages with GPU, local storage, ARM, bare-metal, free-tier, and missing optional fields; verify family sorting; and validate no-credential skip behavior.
