# File Research: sources/local-fs/ocfs2-tools/include/o2cb/ocfs2_heartbeat.h

This header defines the on-disk heartbeat block layout shared with the OCFS2 heartbeat subsystem.

Key structure:
- `struct o2hb_disk_heartbeat_block` contains sequence number, node id, checksum, generation, and dead timeout milliseconds.

Integration notes:
- Uses fixed-size endian-annotated integer types.
- Consumed by userspace code that reads or writes heartbeat region blocks.
