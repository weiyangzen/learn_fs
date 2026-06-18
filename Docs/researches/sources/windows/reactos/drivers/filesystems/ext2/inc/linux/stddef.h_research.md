# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/stddef.h

This small compatibility header defines boolean enum constants and `offsetof` when not already available.

Key definitions:
- Include guard `_LINUX_STDDEF_H`.
- Anonymous enum sets `false = 0` and `true = 1`.
- Defines `offsetof(TYPE, MEMBER)` as `((size_t) &((TYPE *)0)->MEMBER)` if absent.

Research notes:
- This is a minimal Linux-style `stddef.h` shim, not a full standard-library replacement.
- The driver also defines an `offsetof` variant in `linux/module.h`, guarded by `#ifndef offsetof`.
