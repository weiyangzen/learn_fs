# sources/test-tools/kdevops/playbooks/roles/terraform/tasks/common/ssh-config.yml

Purpose: generates controller SSH config entries for Terraform-provisioned nodes.

Important APIs/types/functions: uses `cloud.terraform.terraform_output` for `controller_ip_map`, `blockinfile` with `ssh_config.j2`, and a second `blockinfile` to add `Include {{ kdevops_ssh_config_prefix }}*` to `~/.ssh/config`.

Control flow: retrieves the Terraform output map, loops over host/IP entries to write managed SSH host blocks into `kdevops_ssh_config`, then ensures the user's main SSH config includes the generated files.

State/persistence behavior: mutates SSH config files on the controller and depends on Terraform output state.

Dependencies/integration: depends on Terraform output `controller_ip_map`, template `ssh_config.j2`, variables `kdevops_ssh_config`, `kdevops_ssh_config_prefix`, and OpenSSH include semantics.

Risks/test signals: malformed Terraform output or template variables can write unusable SSH entries. Test signals are generated host blocks, include directive presence, and successful SSH to provisioned nodes.
