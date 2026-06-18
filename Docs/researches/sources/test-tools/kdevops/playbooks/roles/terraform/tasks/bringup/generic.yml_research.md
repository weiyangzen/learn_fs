# sources/test-tools/kdevops/playbooks/roles/terraform/tasks/bringup/generic.yml

Purpose: generic Terraform bringup for providers that do not need custom preflight logic.

Important APIs/types/functions: uses `cloud.terraform.terraform` with `terraform_binary_path`, `state: present`, and provider project path.

Control flow: one module invocation initializes/applies the provider directory.

State/persistence behavior: creates Terraform working directory metadata, state, and provider cloud resources.

Dependencies/integration: called by `bringup/main.yml` when provider is not Lambda Labs or DataCrunch. Depends on `cloud.terraform` collection and `topdir_path`.

Risks/test signals: generic path lacks provider-specific capacity or credential validation. Test signals are module success and active resources in Terraform state.
