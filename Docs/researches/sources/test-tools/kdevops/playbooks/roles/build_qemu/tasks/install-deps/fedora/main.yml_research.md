<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/install-deps/fedora/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/install-deps/fedora/main.yml

Source read: complete file, 271 lines, 6055 bytes, sha256 `69abb67030010304`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/install-deps/fedora/main.yml_research.md`.

Purpose: Fedora-specific QEMU dependency installation with an initial binary presence check.

Important APIs/types/functions: `ansible.builtin.command: which qemu-system-x86_64` registers `qemu_present`; `ansible.builtin.dnf` installs a very large Fedora package set spanning compiler tools, Meson/Ninja, GTK/SDL/SPICE/VTE, gluster, RDMA, liburing, Xen, Sphinx docs, tracing, valgrind, virgl, USB redirection, and storage/network libraries.

Control flow: verify whether QEMU is already in PATH, treating rc 1 as changed but not failed; then install the package list.

State and persistence behavior: changes dnf package state significantly. The verify task only records state; it does not gate the install inside this file.

Dependencies and integration: selected specifically when `ansible_facts['distribution']|lower == 'fedora'`, separate from generic RedHat handling.

Risks: enormous package footprint, duplicated entries, and version-pinned names such as `pkgconf-1.8.0` can break across Fedora releases. The verification result is not used locally to skip installation.

Test signals: Fedora runs should complete dnf dependency installation and then allow QEMU configure/build without subproject downloads.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/install-deps/fedora/main.yml -->
