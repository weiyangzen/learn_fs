# File Research: sources/local-fs/ntfs-3g/libntfs-3g/ioctl.c

## Purpose
Implements NTFS-3G ioctl dispatch, currently centered on Linux `FITRIM` support when both `FITRIM` and `BLKDISCARD` are available.

## Main Interfaces
- `ntfs_ioctl()` dispatches supported ioctls and returns negative errno-style failures.
- `fstrim()` scans the volume bitmap and issues discard requests for free cluster ranges.
- `fstrim_clusters()` sends `BLKDISCARD` to the backing block device.
- `fstrim_limits()` reads discard alignment, granularity, and max-byte limits from `/sys/dev/block`.
- `read_line()` and `read_u64()` read sysfs numeric attributes.
- `align_up()` and `align_down()` align cluster ranges to device discard granularity.

## Control Flow
`ntfs_ioctl()` accepts `FITRIM`, validates inode/data, calls `fstrim()`, and writes actual trimmed byte count back to `struct fstrim_range.len`. `fstrim()` rejects non-default start/length/minlen options, requires a block device, reads discard limits, syncs the device, scans `$BITMAP` in 4096-byte chunks, finds contiguous free cluster runs, granularity-aligns them, caps requests by `discard_max_bytes`, then issues discard.

## Integration Points
Uses `ntfs_attr_pread()` on `vol->lcnbmp_na`, `ntfs_bit_get()` bitmap helpers, `ntfs_device_sync()`, device `d_ops->ioctl`, and NTFS volume cluster sizing.

## Risks and Invariants
- FITRIM only supports full-volume trim with default offset/length and `minlen <= cluster_size`.
- Non-block-device backing stores return `-EOPNOTSUPP`.
- Sysfs probing treats missing discard files as “discard unavailable,” not fatal.
- Count calculation reads whole bitmap bytes; correctness depends on cluster count and bitmap sizing consistency.
