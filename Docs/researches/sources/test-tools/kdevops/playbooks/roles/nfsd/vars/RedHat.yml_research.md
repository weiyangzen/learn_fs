<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfsd/vars/RedHat.yml -->
# sources/test-tools/kdevops/playbooks/roles/nfsd/vars/RedHat.yml

Purpose: provides RedHat-specific NFS server package lists and filesystem userspace package mappings.

Important APIs/types/functions: variables/facts `nfsd_packages`, `fstype_userspace_progs`, `btrfs`, `ext4`, `xfs`, `pipefs_directory`.

Control flow: Variables are loaded by install-deps tasks through `first_found` and then consumed for package installation.

State and persistence behavior: No persistent state; only package variable definitions.

Dependencies and integration points: Integrated with `nfsd` dependency installation and filesystem selection.

Risks: Incorrect package names block NFS setup or filesystem formatting. Suse naming differs from Debian/RedHat for btrfs tools.

Test signals: Signals are package install success and correct package chosen for btrfs, ext4, and xfs.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfsd/vars/RedHat.yml -->
