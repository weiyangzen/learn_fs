# File Research: sources/local-fs/e2fsprogs/misc/fsmap.h

## Purpose
Compatibility header defining `FS_IOC_GETFSMAP` userspace structures and constants when the platform headers do not provide them.

## Key Elements
Defines `struct fsmap`, `struct fsmap_head`, `fsmap_sizeof`, and `fsmap_advance`. Provides header/output flags, record flags for preallocation/attribute fork/extent map/shared/special owner/last, special owner helpers, and the ioctl number.

## Dependencies
Assumes Linux-style integer types such as `__u32` and `__u64` plus ioctl macros are already available from including context.

## Behavior/Risks
Definitions are guarded by `#ifndef FS_IOC_GETFSMAP`, so system headers win when available. This is a compatibility surface for code that needs stable fsmap ABI definitions across older build environments.
