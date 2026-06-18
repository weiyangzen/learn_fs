# File Research: sources/os/linux/linux/fs/ocfs2/ocfs1_fs_compat.h

Role: Defines legacy OCFS1-compatible sector layouts that OCFS2 writes at the start of a volume so OCFS1 tools/drivers can detect the partition and fail cleanly instead of mis-mounting it.

Key contents:
- OCFS1 size constants for volume signature, mount point, volume ID, label, and cluster name.
- OCFS1 version constants: major `2`, minor `0`, signature `"OracleCFS"`.
- `struct ocfs1_vol_disk_hdr`: sector-0 OCFS1 volume header with version, signature, mount point, size/offset fields, cluster sizing, node count, config offsets, and mount/exclusive fields.
- `struct ocfs1_disk_lock`: legacy disk lock format embedded in the volume label sector, with master, lock byte, timestamps, node numbers, node map, and sequence number.
- `struct ocfs1_vol_label`: sector-1 label block containing the disk lock, volume label, volume ID, and cluster name fields.

Design notes:
- These are compatibility disk structures, not active OCFS2 metadata.
- The explicit padding in `ocfs1_disk_lock` preserves the old layout while making alignment visible in C.
