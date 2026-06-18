# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/Makefile

Kernel module makefile for the HAMMER2 VFS implementation.

Key responsibilities:
- Builds the `hammer2` kernel module.
- Adds the main HAMMER2 source directory plus bundled `zlib` and `xxhash` directories to `.PATH`.
- Enables `-DINVARIANTS` for the module build.
- Lists HAMMER2 VFS, vnode, inode, chain, flush, freemap, cluster, ioctl, messaging, compression, I/O, synchronization, admin, bulkfree, and strategy implementation files.
- Builds prefixed or locally namespaced compression/hash support from HAMMER2's bundled zlib and xxhash sources.
- Includes DragonFly's `bsd.kmod.mk` kernel-module rules.

Dependencies:
- Depends on the DragonFly kernel module build system.
- Depends on HAMMER2 sources in the same directory and bundled `zlib`/`xxhash` implementation files.
- Comments explain that `Z_PREFIX` and `XXH_NAMESPACE` are defined in the vendored headers directly so HAMMER2 can also be specified via `conf/files`.

Notable risks:
- Compression/hash symbol prefixing is intentionally managed in headers rather than this makefile; changing one side without the other can create kernel symbol conflicts.
- `KCFLAGS+= -DINVARIANTS` makes this module build with extra assertions enabled, which can alter behavior compared with a non-invariant production build.
