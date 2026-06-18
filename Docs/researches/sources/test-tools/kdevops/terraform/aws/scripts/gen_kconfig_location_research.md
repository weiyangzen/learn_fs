# sources/test-tools/kdevops/terraform/aws/scripts/gen_kconfig_location

## Purpose
This script discovers AWS regions and availability zones and renders Kconfig or raw output for selecting Terraform AWS resource locations.

## Important APIs, Types, And Functions
`get_region_info()` combines a region record with its availability zones, skips not-opted-in regions, and returns endpoint, opt-in status, and zone metadata. `output_region_kconfig()` renders `zone.j2` for one region. `output_regions_kconfig()` renders `regions.j2` with the default region. `output_locations_kconfig()` renders all regions plus zone sections, using a 20-worker thread pool for per-region zone discovery. Raw output functions print tables. `parse_arguments()` supports region lookup, `--regions`, `--format`, and `--quiet`.

## Control Flow
`main()` validates credentials with optional skip-on-absent behavior, fetches all regions, then either lists regions, details a specific region, or emits the complete locations menu. Full Kconfig output is deterministic: the top-level regions menu follows sorted region order, and zone sections are printed in the original region list order after parallel discovery completes.

## State And Persistence
The script writes generated content to stdout only. It reads AWS config/credentials and live EC2 region/AZ state. No cache is maintained.

## Dependencies And Integration Points
It depends on `aws_common.py`, boto3 EC2 `describe_regions`/`describe_availability_zones`, Jinja templates `regions.j2` and `zone.j2`, and the AWS Kconfig wrapper. Generated symbols are later consumed by Terraform variable generation.

## Risks And Test Signals
All-region availability-zone discovery can be slow or rate-limited. Opt-in statuses differ by account, so generated menus are account-specific. The zone query currently only includes `availability-zone`, not local/wavelength zones. Tests should mock opted-in and not-opted-in regions, empty zone lists, API errors, default-region conversion, template rendering, and no-credential exit 0.
