# File Research: sources/local-fs/f2fs-tools/mkfs/f2fs_format_utils.c

Provides mkfs discard/trim helpers for regular files, block devices, and zoned devices.

Key responsibilities:
- `trim_device()` skips aliased devices, stats the target, and computes the full device byte range.
- For regular files, attempts `fallocate(FALLOC_FL_PUNCH_HOLE | FALLOC_FL_KEEP_SIZE)` when supported.
- For block devices:
  - In zoned mode, calls `f2fs_reset_zones()`.
  - Otherwise tries secure discard (`BLKSECDISCARD`) first, then ordinary discard (`BLKDISCARD`).
- Stub `trim_device()` returns success when no supported discard API is available.
- Android-only `is_wiped_device()` checks whether the first 16 MiB of the first device is already zero and can skip trimming.
- `f2fs_trim_devices()` iterates all configured devices, trims those not already wiped, sets `c.trimmed`, and fails on trim errors.

Dependencies:
- Uses global `c`, `struct device_info`, Linux `BLKDISCARD` / `BLKSECDISCARD`, fallocate punch-hole flags, and zoned reset helpers.
- Public prototypes are declared in `f2fs_format_utils.h`.

Behavioral notes:
- Discard failures are often logged as informational and not fatal unless the device type is unsupported or the outer helper returns failure.
- Alias devices are deliberately not discarded because their contents are represented by alias inodes rather than normal free space.
