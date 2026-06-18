# File Research: sources/local-fs/dosfstools/src/blkdev/linux_version.c

Small Linux kernel-version parser.

Behavior:
- `get_linux_version()` caches its result in a static `kver`.
- Calls `uname()`, parses `uts.release` as `major.minor.teeny`, and returns `KERNEL_VERSION(major, minor, teeny)`.
- Returns cached `0` on `uname()` or parse failure.

Consumers:
- `blkdev_get_size()` uses this to avoid Linux kernels with broken `BLKGETSIZE64` behavior.
