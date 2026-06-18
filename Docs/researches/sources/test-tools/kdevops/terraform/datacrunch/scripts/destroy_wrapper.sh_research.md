# sources/test-tools/kdevops/terraform/datacrunch/scripts/destroy_wrapper.sh

## Purpose
This Bash wrapper runs `terraform destroy` for DataCrunch and keeps or clears local OS-volume cache records according to the configured keep-volumes setting.

## Important APIs, Types, And Functions
It computes the same paths as `apply_wrapper.sh`, sources `.config`, derives `KEEP_VOLUMES`, validates `CONFIG_KDEVOPS_HOSTS_PREFIX`, optionally gathers instance hostnames from `terraform output -json`, runs `terraform destroy "$@"`, and then either lists preserved cache entries or deletes mappings for destroyed instances with `volume_cache.py delete`.

## Control Flow
The wrapper prints warnings when keep-volumes is disabled, captures existing instance names before destruction when Terraform output is available, runs destroy, and post-processes cache state only if destroy exits 0. KEEP=yes preserves cache and displays it; KEEP=no deletes cache mappings for known instance names.

## State And Persistence
It mutates remote infrastructure via Terraform destroy. Local persistent side effects are deletion or preservation of cache mappings under `~/.cache/kdevops/datacrunch/<prefix>.yml`. It reads `.config`, Terraform output/state, and cache files.

## Dependencies And Integration Points
It depends on Bash, Terraform, Python 3, the `instance_details` Terraform output contract, and `volume_cache.py`. It integrates with DataCrunch lifecycle automation and the `TERRAFORM_DATACRUNCH_KEEP_VOLUMES` Kconfig option.

## Risks And Test Signals
The comments note DataCrunch may automatically delete OS-NVMe volumes unless detached, so preserving only the cache may not guarantee actual volume reuse. Like apply, it hardcodes `terraform`. If `terraform output` fails, `instance_list` may be unset and cache clearing becomes incomplete. Tests should cover KEEP yes/no, absent output, destroy failure preserving cache, malformed output, multiple hostnames, and fake `volume_cache.py` calls.
