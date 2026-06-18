# sources/test-tools/kdevops/playbooks/terraform.yml

Purpose: wrapper playbook for Terraform infrastructure lifecycle and SSH access management.

Important APIs/types/functions: targets `localhost` and invokes role `terraform`.

Control flow: executes Terraform role locally for bringup/status/destroy operations.

State/persistence behavior: delegated to Terraform role, including cloud resources, Terraform state, and local SSH config.

Dependencies/integration: depends on localhost controller environment, Terraform binary, cloud credentials, and role variables.

Risks/test signals: local controller mutations and cloud resource cost/destruction are the major risks. Test signals are Terraform state and SSH config output.
