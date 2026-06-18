# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/compiler.h

Small compiler-compatibility header. It defines `__GNUC_PREREQ` when missing and provides `container_of`.

For GCC, `container_of` uses `__typeof__` to type-check the member pointer before subtracting `offsetof(type, member)`. For non-GCC compilers, it uses a simpler cast-based implementation.

Dependencies: `<stddef.h>` for `offsetof`.

Implementation notes:
- Header guard is `_EXT2FS_COMPILER_H`.
- This is infrastructure used by intrusive data structures and other low-level helpers.
