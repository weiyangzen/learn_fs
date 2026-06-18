<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/btrfs_progs/tasks/install-deps/debian/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/btrfs_progs/tasks/install-deps/debian/main.yml

Source read: complete file, 22 lines, 496 bytes, sha256 `330a058aed97b947`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/btrfs_progs/tasks/install-deps/debian/main.yml_research.md`.

Purpose: Debian-family dependency installation for building btrfs-progs from source.

Important APIs/types/functions: `ansible.builtin.apt` updates the package cache and installs `libext2fs-dev`, `pkg-config`, `libblkid-dev`, `libzstd-dev`, `libudev-dev`, and `liblzo2-dev`. Tasks use `become: true` with sudo and tags `btrfs-progs`, `update-cache`, and `build-deps`.

Control flow: first refresh apt metadata, then install the build dependency set. This file is imported only when the dispatcher sees `ansible_facts['os_family']|lower == 'debian'`.

State and persistence behavior: mutates apt cache and package database. Installed development headers persist on the target VM.

Dependencies and integration: supports `btrfs_progs/tasks/main.yml` before `autogen.sh`, `configure`, and `make`. It assumes Debian/Ubuntu package names and apt availability.

Risks: no retry wrapper around apt operations. Missing `git`, compiler, automake/autoconf, or make may be supplied elsewhere; if not, source builds can fail after this dependency step.

Test signals: run with the role tag on Debian/Ubuntu and confirm apt reports the listed packages present before configure.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/btrfs_progs/tasks/install-deps/debian/main.yml -->
