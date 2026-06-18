# sources/test-tools/kdevops/playbooks/roles/terraform/tasks/bringup/main.yml

Purpose: provider dispatcher for Terraform bringup.

Important APIs/types/functions: conditional `include_tasks` for `lambdalabs.yml`, `datacrunch.yml`, or `generic.yml`.

Control flow: selects Lambda Labs tasks for `kdevops_terraform_provider == 'lambdalabs'`, DataCrunch tasks for `datacrunch`, and generic tasks otherwise.

State/persistence behavior: no direct state except delegated provider bringup side effects.

Dependencies/integration: driven by generated `kdevops_terraform_provider`.

Risks/test signals: provider string drift routes to generic path and bypasses required custom validation. Test signals are correct include path and provider-specific status output.
