# sources/test-tools/kdevops/playbooks/update_ssh_config_nixos.yml

Purpose: standalone playbook that generates a kdevops SSH key and SSH config entries for NixOS VMs.

Important APIs/types/functions: `file`, `stat`, `ssh-keygen`, permission setting, shell `virsh list`, and `blockinfile` into `{{ topdir_path }}/.ssh/config`.

Control flow: creates `.ssh`, checks/generates RSA key, sets key permissions, lists libvirt VM names matching the host prefix or `nixos`, and writes an Ansible-managed SSH config block for each VM using hostvars/default IP.

State/persistence behavior: creates `topdir_path/.ssh/kdevops_id_rsa(.pub)` and mutates `topdir_path/.ssh/config`.

Dependencies/integration: depends on libvirt `virsh`, `libvirt_uri`, `kdevops_host_prefix`, `topdir_path`, and hostvars for VM addresses.

Risks/test signals: defaulting HostName to `192.168.100.2` can create wrong entries if hostvars are missing; key generation is not hashed per directory. Test signals are generated key/config and successful SSH to NixOS VMs.
