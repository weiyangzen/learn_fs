# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/dosfsck.h

This header is a bridge between ReactOS `vfatlib.h` and dosfsck-derived checker modules.

Core contents:
- Redefines `off_t` as `__int64` through a macro.
- Includes checker headers: common, fsck.fat structures, I/O, boot, check, FAT, file selection, and LFN support.

Risk points:
- Macro-defining `off_t` can collide with real typedefs or external headers.
- It centralizes many dependencies, so include order matters.
