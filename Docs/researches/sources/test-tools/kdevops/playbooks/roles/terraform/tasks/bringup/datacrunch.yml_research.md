# sources/test-tools/kdevops/playbooks/roles/terraform/tasks/bringup/datacrunch.yml

Purpose: DataCrunch-specific Terraform bringup, including external provider installation, capacity-aware GPU instance selection, dev-overrides initialization, and apply with tier fallback.

Important APIs/types/functions: uses `set_fact`, `stat`, shell download/unzip of `terraform-provider-datacrunch`, helper scripts `datacrunch_select_tier.py` and `datacrunch_check_capacity.py`, `lineinfile` edits to `terraform.tfvars`, `terraform state list`, temporary Terraform provider config generation, and shell `terraform apply`.

Control flow: normalizes architecture, installs provider if missing, optionally resolves wildcard tier to instance/location, validates capacity, auto-selects location for explicit instance types, updates tfvars, skips apply when state already contains resources, initializes external provider around dev overrides by hiding real `.tf` files, then applies. For wildcard tiers the apply loop retries with lower-tier selections when capacity/provisioning fails.

State/persistence behavior: writes provider binaries under `~/.terraform.d/plugins`, mutates `terraform/<provider>/terraform.tfvars`, creates `.terraform` and `.terraform.lock.hcl`, and provisions cloud resources recorded in Terraform state.

Dependencies/integration: depends on GitHub releases, DataCrunch helper scripts/API credentials, Terraform CLI, provider-specific tfvars, `topdir_path`, and generated `terraform_datacrunch_*` variables.

Risks/test signals: high-risk mutations include editing tfvars in place, hiding/restoring Terraform files, and retrying cloud provisioning. Capacity checks are time-sensitive. Test signals are provider binary existence, successful state list/init, selected instance/location messages, Terraform apply success, and non-empty Terraform state.
