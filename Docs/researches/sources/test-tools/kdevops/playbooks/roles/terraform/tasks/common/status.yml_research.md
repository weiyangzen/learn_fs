# sources/test-tools/kdevops/playbooks/roles/terraform/tasks/common/status.yml

Purpose: reports current Terraform resource and controller IP status.

Important APIs/types/functions: block with `cloud.terraform.terraform_output`, `meta: end_play`, shell `terraform state list`, and debug output.

Control flow: reads `controller_ip_map`; if Terraform state is empty or missing it ends the play; otherwise counts resources via `terraform state list` and displays resource count plus IP map.

State/persistence behavior: read-only against Terraform state.

Dependencies/integration: included after bringup/status operation by Terraform role; depends on Terraform CLI and output state.

Risks/test signals: warning-based empty-state detection can miss some failure modes. Test signals are displayed active resource count and controller IP map.
