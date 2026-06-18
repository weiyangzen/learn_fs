# File Research: sources/os/linux/linux/fs/ext4/fsmap.c

Implements ext4 support for `FS_IOC_GETFSMAP`, reporting filesystem physical-space mappings for the data device and optional external journal device.

Key behavior:
- Converts between public `struct fsmap` byte units and internal `struct ext4_fsmap` block units.
- Uses `struct ext4_getfsmap_info` to track query keys, formatter callback, current device, current block group, next expected block, fixed metadata, retained free extent, and final-record state.
- Reports gaps between known records as `EXT4_FMR_OWN_UNKNOWN`.
- Supports count-only mode when `fmh_count == 0`.
- Builds and reports fixed metadata records for:
  - superblock copies
  - group descriptors
  - reserved GDT blocks
  - block bitmaps
  - inode bitmaps
  - inode tables
- Sorts and merges adjacent fixed metadata records before query output.
- Merges fixed metadata with free-space records from mballoc query callbacks.
- Coalesces free extents that cross block-group boundaries.
- `ext4_getfsmap_logdev()` fabricates one mapping for an external journal device.
- `ext4_getfsmap_datadev()` clamps query ranges to filesystem data blocks, converts global keys to block-group keys, queries each block group through `ext4_mballoc_query_range()`, and emits final unknown tail gaps.
- Validates requested device ids against the filesystem block device and external journal device.
- Validates low/high fsmap key ordering.
- `ext4_getfsmap()` sorts per-device handlers, supports continuation via nonzero low-key length, dispatches matching device handlers, and marks device ids as present in output flags.

Important interactions:
- Uses mballoc’s range-query callbacks for free-space discovery.
- Uses ext4 group descriptor helpers to locate fixed metadata.
- Uses `trace_ext4_fsmap_*` events for low/high keys and emitted mappings.
