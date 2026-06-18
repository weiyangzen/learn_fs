# sources/test-tools/kdevops/playbooks/datacrunch_volume_cache.yml

Purpose: manages DataCrunch OS/NVMe volume cache mappings so cloud volumes can be reused across destroy/recreate cycles when keep-volumes mode is enabled.

Important APIs/types/functions: local play with variables `volume_cache_script`, `terraform_dir`, and `action`. Uses `fail`, `terraform output -json`, `set_fact`, and `python3 volume_cache.py` subcommands `save`, `delete`, and `list`.

Control flow: verify provider is `datacrunch`; for `save`, require `terraform_datacrunch_keep_volumes`, read Terraform outputs, extract `instance_details.value`, and save each non-empty `os_volume_id`. For `delete`, iterate `kdevops_nodes`. For `list`, display cached mappings.

State/persistence behavior: mutates an external cache managed by `terraform/datacrunch/scripts/volume_cache.py`; does not alter Terraform state directly.

Dependencies/integration: integrates Terraform provider output, host prefix naming, DataCrunch volume retention, and kdevops node inventory variables.

Risks/test signals: action help mentions `load`, but implemented actions are save/delete/list. Cache correctness depends on Terraform output shape and stable node names. Test signals are provider guard failures when misused, saved IDs for each instance, and list output matching expected mappings.
