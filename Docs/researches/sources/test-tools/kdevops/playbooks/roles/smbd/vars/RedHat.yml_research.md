<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/smbd/vars/RedHat.yml -->
# sources/test-tools/kdevops/playbooks/roles/smbd/vars/RedHat.yml

Purpose: defines RedHat-specific Samba package lists and filesystem userspace tool mappings.

Important APIs/types/functions: variables/facts `smbd_packages`, `fstype_userspace_progs`, `btrfs`, `ext4`, `xfs`.

Control flow: Loaded by SMB install-deps tasks through `first_found`.

State and persistence behavior: No runtime state beyond variable values.

Dependencies and integration points: Supports package installation for `smbd` role.

Risks: Incorrect package names block Samba or formatting setup; Suse btrfs package name differs.

Test signals: Signals are successful install for configured `smbd_share_fstype`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/smbd/vars/RedHat.yml -->
