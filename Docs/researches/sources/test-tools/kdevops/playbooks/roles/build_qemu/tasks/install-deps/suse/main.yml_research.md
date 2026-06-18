<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/install-deps/suse/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/install-deps/suse/main.yml

Source read: complete file, 421 lines, 9853 bytes, sha256 `63bacada8a90b5b6`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/install-deps/suse/main.yml_research.md`.

Purpose: SUSE-family QEMU build dependency installation, currently targeting Tumbleweed with a broad package closure.

Important APIs/types/functions: `set_fact` classifies SLE/Leap/Tumbleweed; `ansible.builtin.package` installs hundreds of packages including compilers, cross toolchains, Meson/Ninja, GTK/SDL/SPICE/VTE, gluster, RDMA, liburing, Xen, Sphinx docs, virgl, USB redirection, CXL-adjacent storage libraries, and X/Wayland development packages. The package task runs only when `is_tumbleweed`.

Control flow: set distro facts, then install the package set for Tumbleweed.

State and persistence behavior: changes zypper/rpm package state heavily and leaves a full QEMU build environment on the host.

Dependencies and integration: imported by QEMU dependency dispatcher for SUSE systems. It assumes Tumbleweed package naming and repository availability.

Risks: Leap/SLE are classified but do not install anything here, so QEMU builds on those systems lack dependencies. The package set is large, version-specific (`python38-*`, `gcc12`), and likely to age quickly.

Test signals: on Tumbleweed, dependency install should complete and QEMU configure should find expected optional features. On Leap/SLE, dry runs should reveal skipped dependency installation as a known gap.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/install-deps/suse/main.yml -->
