# File Research: sources/local-fs/ocfs2-tools/libtools-internal/scandisk.c

Implements Linux block-device discovery and classification for internal tooling.

Key responsibilities:
- Maintains a cached linked list of devices keyed by major/minor.
- Scans `/sys/block`, `/proc/partitions`, `/dev`, `/proc/mdstat`, and `/proc/devices`.
- Associates multiple paths with each device.
- Marks sysfs attributes such as removable, holders, slaves, and disk-like status.
- Marks device-mapper, mdraid, and powerpath devices.
- Allows callers to run a custom filter over the discovered list.

Important functions:
- `scan_for_dev(devlisthead, timeout, filter, filter_args)`: public scanner/cache entry point.
- `free_dev_list()`: public cleanup.
- `scansysfs()`: recursive `/sys/block` scanner.
- `scanprocpart()`: parses `/proc/partitions`.
- `lsdev()`: recursive `/dev` scanner for block devices and symlinks to block devices.
- `scanmdstat()`, `scanmapper()`, `scanpower()`: classify stacking technologies.

Dependencies:
- Linux procfs/sysfs conventions.
- `sys/sysmacros.h` major/minor helpers.
- Internal `tools-internal/scandisk.h`.

Research notes:
- Cache expiration is based on `cache_timestamp` and `cache_timeout`; nonpositive timeout means no expiration.
- Device discovery is tolerant of missing sources, but aborts on allocation failures.
- The debug executable demonstrates filtering for top-level disks with `/dev/sd*` or `/dev/mapper/*` paths.
