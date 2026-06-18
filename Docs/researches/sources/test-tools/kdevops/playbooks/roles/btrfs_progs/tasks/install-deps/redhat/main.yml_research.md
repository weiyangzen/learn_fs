<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/btrfs_progs/tasks/install-deps/redhat/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/btrfs_progs/tasks/install-deps/redhat/main.yml

Source read: complete file, 14 lines, 318 bytes, sha256 `c06ea188ec89d827`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/btrfs_progs/tasks/install-deps/redhat/main.yml_research.md`.

Purpose: Red Hat family package installation for btrfs-progs source builds.

Important APIs/types/functions: `ansible.builtin.dnf` installs `e2fsprogs-devel`, `libblkid-devel`, `libuuid-devel`, `libzstd-devel`, `systemd-devel`, and `lzo-devel` with sudo.

Control flow: a single package task runs when imported by the OS dispatcher on RedHat-family systems.

State and persistence behavior: updates the rpm/dnf package database by ensuring development packages are present.

Dependencies and integration: prepares for btrfs-progs `autogen.sh` and `configure`. The role assumes package naming is valid across Red Hat-like distributions.

Risks: package names such as `systemd-devel` and `lzo-devel` vary across old enterprise releases and may need CodeReady/CRB repos enabled. No retry or cache refresh is included here.

Test signals: on Fedora/RHEL/CentOS/Oracle Linux, dnf should install the list and a subsequent `./configure --disable-documentation --enable-experimental` should locate blkid, uuid, zstd, udev/systemd, lzo, and ext2fs headers.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/btrfs_progs/tasks/install-deps/redhat/main.yml -->
