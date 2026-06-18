# sources/test-tools/kdevops/playbooks/roles/update_etc_hosts/defaults/main.yml

Purpose: default booleans for host-file update behavior.

Important APIs/types/functions: defines `terraform_private_net_enabled: false` and `kdevops_enable_guestfs: false`.

Control flow: no executable flow; these defaults control conditionals in the role tasks.

State/persistence behavior: no direct state.

Dependencies/integration: consumed by `tasks/main.yml` and overridden by generated config for Terraform private networks or guestfs.

Risks/test signals: wrong defaults/overrides select public vs private IP handling. Test signal is resulting `/etc/hosts` line content.
