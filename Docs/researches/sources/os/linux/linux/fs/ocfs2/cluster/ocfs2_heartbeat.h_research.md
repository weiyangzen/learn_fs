# File Research: sources/os/linux/linux/fs/ocfs2/cluster/ocfs2_heartbeat.h

Userspace/kernel shared on-disk heartbeat structure header.

Defines:
- `struct o2hb_disk_heartbeat_block`:
  - `hb_seq`: heartbeat sequence timestamp.
  - `hb_node`: node number.
  - padding.
  - `hb_cksum`: CRC32 over the heartbeat block with checksum field zeroed.
  - `hb_generation`: nonzero generation distinguishing region starts/stops.
  - `hb_dead_ms`: advertised dead timeout in milliseconds.

Usage:
- Written and read by `heartbeat.c` in each node’s disk slot.
- Generation zero is used as clean down notification.
