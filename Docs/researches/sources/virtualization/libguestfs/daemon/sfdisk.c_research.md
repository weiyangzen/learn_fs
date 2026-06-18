# File Research: sources/virtualization/libguestfs/daemon/sfdisk.c

Legacy `sfdisk` partitioning wrappers.

Important behavior:
- Shared `sfdisk` helper builds a fixed-size shell command string and writes partition lines to stdin.
- Explicitly bounds `extra_flag` and device length before appending to the command buffer.
- After successful `sfdisk`, calls `blockdev --rereadpt` and `udev_settle`.
- Provides full-table, single-partition `-N`, megabyte-unit `-uM`, list, kernel geometry, and disk geometry APIs.
- Query variants use argument-vector `command`.

Filesystem relevance: older partition table creation/query path complementary to `parted.c`.
