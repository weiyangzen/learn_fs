# sources/test-tools/kdevops/playbooks/roles/terraform/defaults/main.yml

Purpose: default variable file for Terraform orchestration.

Important APIs/types/functions: defines `ssh_config_kexalgorithms` and `terraform_binary_path`.

Control flow: no executable flow; values are consumed by Terraform task files and SSH config templates/modules.

State/persistence behavior: no direct state. Defaults influence which Terraform binary is invoked and SSH template content.

Dependencies/integration: integrates with `cloud.terraform` modules, role task shell commands, and generated extra vars.

Risks/test signals: incorrect `terraform_binary_path` breaks every lifecycle task. Test signals are successful module calls and shell `terraform` invocations.
