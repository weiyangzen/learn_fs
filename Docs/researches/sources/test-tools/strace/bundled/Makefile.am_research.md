<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/Makefile.am -->
# sources/test-tools/strace/bundled/Makefile.am

Purpose: Automake input listing bundled Linux UAPI header snapshots included in strace source distributions.

Important declarations: `EXTRA_DIST` enumerates Linux license files and many `linux/include/uapi` and architecture-specific headers. The listed subset includes fcntl variants, hugetlb encoding, audit, block, BSG, Btrfs, cgroup, netlink, io_uring, seccomp, and many more. `dist-hook` symlinks `asm-generic` as `linux/include/uapi/asm` inside the dist directory.

Control flow: declarative distribution list plus one dist hook.

State and persistence: affects tarball contents and creates a symlink during `make dist`.

Dependencies and integration: feeds strace decoders that need stable UAPI constants independent of host headers.

Risks: manual `EXTRA_DIST` can miss newly bundled headers or include stale ones. Symlink creation can behave differently on platforms without symlink support. Test signals: `make distcheck` should include every referenced header and produce the expected `asm` symlink.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/Makefile.am -->
