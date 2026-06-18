<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfsd/tasks/install-deps/debian/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/nfsd/tasks/install-deps/debian/main.yml

Purpose: installs NFS server dependencies for debian family systems and dynamically includes filesystem userspace tools for the configured export filesystem.

Important APIs/types/functions: modules `ansible.builtin.include_vars`, `ansible.builtin.set_fact`, `ansible.builtin.apt`; variables/facts `params`, `fsprogs`, `nfsd_packages`, `become_method`, `update_cache`; tasks `Get OS-specific variables`, `Determine which fsprogs package is needed for "{{ nfsd_export_fstype }}"`, `Add {{ fsprogs }} to the nfsd packages list`, `Add gssproxy to the nfsd packages list`, `Install nfsd dependencies`.

Control flow: Loads OS vars, computes the package needed for `nfsd_export_fstype`, appends it to `nfsd_packages` when present, then installs with the distro package manager.

State and persistence behavior: Mutates target package state and the transient `nfsd_packages` fact.

Dependencies and integration points: Included by `nfsd/tasks/main.yml`. Depends on `vars/<OS>.yml` package maps.

Risks: Unknown filesystem types can leave `fsprogs` empty and skip required mkfs tools. RedHat/Suse package names differ.

Test signals: Signals are successful install for btrfs/ext4/xfs exports and no duplicate package-list failures on repeat runs.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfsd/tasks/install-deps/debian/main.yml -->
