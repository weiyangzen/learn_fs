# File Research: sources/os/bsd/netbsd-src/lib/Makefile

Top-level NetBSD `lib` build orchestrator. It orders `csu`, compiler runtime libraries, and `libc` before the rest of the library tree, then uses `.WAIT` dependency barriers to sequence libraries by link-time dependency.

Important filesystem-adjacent entries include `libpuffs`, `libperfuse`, `librefuse`, `libquota`, `libdm`, rump libraries, ZFS support libraries, LVM2, and external archive/compression libraries. Build inclusion is controlled by feature knobs such as `MKRUMP`, `MKZFS`, `MKLVM`, `MKNPF`, `MKDTRACE`, `MKPAM`, `MKGCC`, and `MKLLVMRT`.

The file ends by including `bsd.buildinstall.mk` and `bsd.subdir.mk`, making it a pure build graph rather than implementation code.
