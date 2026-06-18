# sources/test-tools/kdevops/terraform/datacrunch/scripts/apply_wrapper.sh

## Purpose
This Bash wrapper runs `terraform apply` for DataCrunch and, when volume preservation is enabled, records OS volume IDs from Terraform output into the kdevops DataCrunch volume cache.

## Important APIs, Types, And Functions
The script computes `SCRIPT_DIR`, `TERRAFORM_DIR`, `VOLUME_CACHE`, and `KDEVOPS_ROOT`; sources `$KDEVOPS_ROOT/.config`; derives `KEEP_VOLUMES` from `CONFIG_TERRAFORM_DATACRUNCH_KEEP_VOLUMES`; and reads `CONFIG_KDEVOPS_HOSTS_PREFIX`. It invokes `terraform apply "$@"`, then on success calls `terraform output -json` and an inline Python JSON parser to extract `instance_details.value[hostname].os_volume_id`, saving each mapping with `volume_cache.py save`.

## Control Flow
With `set -e`, missing config or failed commands abort. The script validates host prefix, prints summary information, changes to the Terraform directory, runs apply, captures status, and only performs cache update when apply succeeded and keep-volumes is yes. It preserves Terraform's exit status.

## State And Persistence
It mutates remote infrastructure through Terraform apply and writes local cache mappings under `~/.cache/kdevops/datacrunch/<prefix>.yml` through `volume_cache.py`. It reads `.config` and Terraform state/output.

## Dependencies And Integration Points
It depends on Bash, Terraform on PATH, Python 3, the DataCrunch Terraform output contract `instance_details`, and `volume_cache.py`. It integrates with kdevops Make targets that should call this wrapper instead of raw Terraform when DataCrunch caching is desired.

## Risks And Test Signals
`set -e` plus command substitution around `terraform output` is handled with an `if`, but other unexpected failures abort. The wrapper hardcodes `terraform` rather than honoring a configured Terraform/OpenTofu binary. Cache update depends on output field shape and silently does nothing when no volume IDs are present. Tests should run with fixture `.config`, fake Terraform script outputs, KEEP on/off, host prefix missing, malformed JSON output, and volume cache save failures.
