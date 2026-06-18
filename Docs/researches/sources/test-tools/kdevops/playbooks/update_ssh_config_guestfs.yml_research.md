# sources/test-tools/kdevops/playbooks/update_ssh_config_guestfs.yml

Purpose: wrapper playbook that updates the controller OpenSSH config for libguestfs kdevops environments.

Important APIs/types/functions: targets `localhost` and invokes `update_ssh_config_guestfs`.

Control flow: delegates to role tasks.

State/persistence behavior: mutates `~/.ssh/config` on the controller.

Dependencies/integration: depends on guestfs-generated SSH config naming.

Risks/test signals: can alter user SSH config. Test signal is correct include directive and SSH connectivity.
