<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/create_partition/tasks/install-deps/redhat/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/create_partition/tasks/install-deps/redhat/main.yml

Source read: complete file, 27 lines, 558 bytes, sha256 `7b798efcfd862c3c`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/create_partition/tasks/install-deps/redhat/main.yml_research.md`.

Purpose: Red Hat family installation of base filesystem tools for partition creation.

Important APIs/types/functions: `ansible.builtin.dnf` installs `xfsprogs` and `e2fsprogs` on all RedHat-family systems, and installs `btrfs-progs` with retries only on Fedora.

Control flow: run base package install with cache update; then, if `ansible_distribution == 'Fedora'`, retry btrfs-progs install up to three times.

State and persistence behavior: mutates dnf package state.

Dependencies and integration: prepares `create_partition` to format XFS/ext filesystems everywhere and btrfs on Fedora.

Risks: non-Fedora RedHat systems do not install btrfs-progs, so `disk_setup_fstype=btrfs` can fail. Cache update on every run may slow playbooks.

Test signals: Fedora run should install all three tool families; RHEL/CentOS with btrfs requested should be tested for expected failure or separate repo support.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/create_partition/tasks/install-deps/redhat/main.yml -->
