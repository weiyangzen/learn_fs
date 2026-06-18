# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/ocfsplist.c

C helper for enumerating partitions and classifying filesystem type/mount state for the GUI.

Key exported function:
- `ocfs_partition_list(func, data, filter, fstype, unmounted, async)`
  - Creates blkid cache.
  - Optionally compiles GLib pattern filter.
  - Builds device/partition grouping from `/proc/partitions`.
  - Walks entries and calls callback with `OcfsPartitionInfo`.

Key internal logic:
- `partition_info_fill`
  - Reads `/proc/partitions`.
  - Groups partitions under disk-like keys.
  - Handles whole-disk entries.
  - Optionally yields to GLib main loop for async UI responsiveness.
- `get_device_fstype`
  - Applies filter.
  - Requires block device and writable mode bits.
  - Skips IDE CD-ROM/tape devices using `/proc/ide/.../media`.
  - Opens device read-write to test accessibility.
  - Delegates type detection to `fstype_check`.
- `fstype_check`
  - Uses blkid to read `TYPE`.
  - If no type and no requested `fstype`, returns:
    - `partition table` if MBR signature is present
    - `unknown` otherwise
- `partition_walk`
  - Uses `ocfs2_check_mount_point` to determine mountpoint/busy state.
  - If `unmounted=True`, reports only unmounted, not busy, and not excluded pseudo-types.

Dependencies:
- GLib
- `libocfs2`
- bundled/system blkid
- `/proc/partitions`

Notable details:
- Opens devices with `O_RDWR` even for type checks.
- The filter is a GLib glob pattern matched against full device path.
- Async mode manually pumps the default GLib main context every fixed number of iterations.
