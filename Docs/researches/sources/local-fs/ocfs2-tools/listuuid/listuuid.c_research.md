# File Research: sources/local-fs/ocfs2-tools/listuuid/listuuid.c

Implements a utility that lists OCFS/OCFS2 UUIDs and labels for devices.

Key responsibilities:
- Parses `/proc/partitions` to build candidate `/dev/<name>` entries.
- Optionally checks a single user-provided device.
- Opens each device as OCFS2 using `ocfs2_open()`.
- Detects OCFS1 via `OCFS2_ET_OCFS_REV`.
- Reads OCFS2 label/UUID from the superblock or OCFS1 label/UUID via compatibility helper.
- Prints a table with device, major/minor, filesystem type, UUID, and label.

Important functions:
- `ocfs2_partition_list()`
- `ocfs2_detect()`
- `ocfs2_print_uuids()`
- `read_options()`
- `main()`

Dependencies:
- `/proc/partitions`.
- `uuid_unparse`.
- `ocfs2_open`, `ocfs2_close`, `ocfs2_get_ocfs1_label`.

Research notes:
- `-a` sets `all_devices`, but the variable is not used by the detection logic in this file.
- If no device argument is supplied, it scans all partitions from `/proc/partitions`.
