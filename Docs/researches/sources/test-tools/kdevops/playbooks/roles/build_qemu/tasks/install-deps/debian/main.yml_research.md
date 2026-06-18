<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/install-deps/debian/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/install-deps/debian/main.yml

Source read: complete file, 75 lines, 1625 bytes, sha256 `108d9cbe4126b381`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/install-deps/debian/main.yml_research.md`.

Purpose: Debian-family QEMU build dependency installation.

Important APIs/types/functions: `ansible.builtin.apt` updates the cache and installs a broad set of QEMU development dependencies: Meson/Ninja/Python/Sphinx, pixman, libfdt, libslirp, liburing, libusb, GTK/SDL/VTE/virgl, storage libraries for gluster/rbd/iscsi/nfs/pmem, RDMA, Xen, SPICE, seccomp, zstd, and documentation tooling.

Control flow: update cache first, then install the package list in one apt task tagged `qemu` and `build-deps`.

State and persistence behavior: persists a large development toolchain and library set on the target.

Dependencies and integration: imported by the build_qemu dependency dispatcher on Debian/Ubuntu and consumed by QEMU `./configure --target-list=... --disable-download`.

Risks: the package set is expansive and may differ across Debian/Ubuntu releases. No retry is present. Some packages are optional for the configured `x86_64-softmmu` target but still installed.

Test signals: after install, QEMU configure should not attempt downloads and should find Meson/Ninja plus the listed optional libraries.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/install-deps/debian/main.yml -->
