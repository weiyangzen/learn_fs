# sources/test-tools/kdevops/playbooks/roles/terraform/tasks/destroy/generic.yml

Purpose: generic Terraform destroy for providers without custom teardown.

Important APIs/types/functions: `cloud.terraform.terraform` with `state: absent`.

Control flow: one module invocation destroys resources in the provider project path.

State/persistence behavior: destroys cloud infrastructure and updates Terraform state.

Dependencies/integration: called by destroy dispatcher for non-DataCrunch providers.

Risks/test signals: destructive action depends entirely on correct provider directory and state. Test signals are module success and empty state.
