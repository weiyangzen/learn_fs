<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/install-deps/redhat/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/install-deps/redhat/main.yml

Source read: complete file, 66 lines, 1427 bytes, sha256 `00f749d8b5494129`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/install-deps/redhat/main.yml_research.md`.

Purpose: generic Red Hat family QEMU build dependency installation for non-Fedora systems.

Important APIs/types/functions: `ansible.builtin.dnf` installs a package list that mirrors the Debian dependency names, including `gnutls-dev`, `libaio-dev`, `libcurl4-gnutls-dev`, `libfdt-dev`, `liburing-dev`, `python3-sphinx-rtd-theme`, `zlib1g-dev`, and others.

Control flow: one dnf task ensures the list is present when imported by the dispatcher.

State and persistence behavior: mutates rpm package state.

Dependencies and integration: intended for RHEL/CentOS/Oracle Linux QEMU source builds.

Risks: many names are Debian-style and likely invalid on RHEL-compatible systems, unlike the Fedora file's native names. CodeReady/CRB repositories may be needed even after names are corrected. No retry or repo enablement occurs here.

Test signals: run on the target non-Fedora RedHat family release; if dnf cannot resolve names, this file needs a package-name translation pass before QEMU builds can be reliable.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/install-deps/redhat/main.yml -->
