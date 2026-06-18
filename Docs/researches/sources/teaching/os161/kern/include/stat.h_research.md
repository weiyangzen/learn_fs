# File Research: sources/teaching/os161/kern/include/stat.h

Provides the kernel-facing `stat` interface by including shared ABI definitions from `kern/stat.h` and shared file-type macros from `kern/stattypes.h`. It maps underscore-prefixed ABI constants to conventional names: `S_IFMT`, `S_IFREG`, `S_IFDIR`, `S_IFLNK`, `S_IFIFO`, `S_IFSOCK`, `S_IFCHR`, and `S_IFBLK`.

This header contains no logic; its role is compatibility and namespace presentation. VFS and device code use these macros to report vnode object types in `stat` data and type checks.

Risk is limited to ABI consistency: these aliases must track the shared `kern/*` definitions used by userland-visible structures.
