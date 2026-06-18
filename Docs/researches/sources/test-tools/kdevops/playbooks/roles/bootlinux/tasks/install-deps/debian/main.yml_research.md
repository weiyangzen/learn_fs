# sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/install-deps/debian/main.yml

This Debian dependency file updates apt metadata and installs packages needed to build and install Linux kernels. The list includes compilers, make, git, bison/flex, bc, libssl/libelf/ncurses development headers, filesystem utilities, mdadm, iSCSI, Python pip, zstd, b4, ccache, rsync, dwarves, and lz4.

Important APIs are `ansible.builtin.apt` with privileged execution. Persistent state is installed packages. Integration points are bootlinux build tasks, Rust dependency role, optional b4 patch application, ccache setup, and kernel packaging/install commands. Risks include package availability differences across Debian/Ubuntu versions, `portmap` being obsolete on some distributions, and no retry logic for apt operations. Test signals should include package resolution on supported releases and verifying `make`, `gcc`, `b4`, `ccache`, and `pahole` are available.
