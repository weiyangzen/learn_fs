# File Research: sources/local-fs/ocfs2-tools/o2cb_ctl/op_start.c

`o2cb` global heartbeat start/stop operations.

Starting heartbeat verifies the cluster exists, the stack is initialized, the cluster is registered, and global heartbeat is enabled. It builds a list of configured heartbeat UUIDs, scans disks to resolve them to devices/descriptors, starts heartbeat on each, and stops active heartbeat regions that were removed from config.

Stopping heartbeat builds minimal fake descriptors for active registered regions and calls `o2cb_stop_heartbeat()` for all regions, or only stale regions during start reconciliation. If a start fails after some devices were started, cleanup stops those started devices.
