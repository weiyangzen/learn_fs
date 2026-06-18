# File Research: sources/os/bsd/freebsd-src/sys/fs/tarfs/tarfs_dbg.h

Compile-time optional debug logging header for tarfs.

Key responsibilities:
- Declares `tarfs_debug` when `TARFS_DEBUG` is enabled.
- Defines bitmask categories for allocation, checksum, filesystem, lookup, vnode, I/O, decompression I/O, decompression index, sparse map, and bounce-buffer diagnostics.
- Provides `TARFS_DPF(category, fmt, ...)` and conditional `TARFS_DPF_IFF(category, cond, fmt, ...)` macros that print only when the matching category bit is enabled.
- Compiles both macros to no-ops when `TARFS_DEBUG` is not enabled.

Dependencies:
- Kernel-only header guarded by `_KERNEL`.
- Runtime sysctl exposure of `tarfs_debug` is in `tarfs_subr.c`.

Notable risks:
- Debug macro category names are concatenated into `TARFS_DEBUG_<category>`, so all call sites must use exactly one of the defined suffixes.
- Debug-only expression arguments are not evaluated in non-debug builds; side effects must never be placed in debug macro arguments.
