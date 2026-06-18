# File Research: sources/local-fs/ocfs2-tools/mounted.ocfs2/mounted.c

OCFS2 volume and mount-state detection utility.

It supports quick mode, which scans a specific device or `/proc/partitions`, reads candidate superblocks at 1K/2K/4K/8K offsets, and prints device, stack, cluster, global-heartbeat flag, UUID, and label. Full mode calls `ocfs2_check_heartbeats()` to inspect heartbeat and slot-map state, then prints nodes that may have the volume mounted.

Device discovery skips tiny devices, maps `dm-N` to `/dev/mapper/*` when possible, removes whole disks when a partition is discovered, and handles common IDE/SCSI whole-disk minor layouts. Full detection can be stale after unclean unmounts because it reports slot-map state without taking cluster locks.
