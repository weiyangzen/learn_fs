# File Research: sources/os/bsd/freebsd-src/sys/sys/_types.h

Core FreeBSD internal type foundation.

Key elements:
- Defines fixed-width internal integer types, pointer-sized types, size/ssize/ptrdiff, VM offset/size, and many system ABI types.
- Includes `machine/_types.h` for target-specific additions.
- Defines filesystem-relevant types including `__blksize_t`, `__blkcnt_t`, `__fflags_t`, `__fsblkcnt_t`, `__fsfilcnt_t`, `__ino_t`, `__mode_t`, `__nlink_t`, `__off_t`, `__dev_t`, and `__daddr_t`.
- Defines ACL internal typedefs, max alignment type, multibyte state, varargs compatibility, and `__INO64`.

Dependencies:
- Compiler width macros and `machine/_types.h`.

Research notes:
- This is the key ABI substrate for almost every other header in the group.
- Comments emphasize preserving exact typedef spellings to avoid ABI and C++ name-mangling breaks.
