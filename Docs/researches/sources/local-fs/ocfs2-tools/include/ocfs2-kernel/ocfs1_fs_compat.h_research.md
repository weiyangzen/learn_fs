# File Research: sources/local-fs/ocfs2-tools/include/ocfs2-kernel/ocfs1_fs_compat.h

This header defines OCFS1 compatibility volume header structures written by OCFS2.

Key content:
- Defines OCFS1 length limits, version constants, and `OCFS1_VOLUME_SIGNATURE`.
- `struct ocfs1_vol_disk_hdr` models the sector-0 OCFS1 volume header, including signature, mount point, offsets, sizes, node counts, and config fields.
- `struct ocfs1_disk_lock` models an OCFS1 disk lock with explicit padding for alignment.
- `struct ocfs1_vol_label` models the sector-1 volume label, including disk lock, label, volume ID, and cluster name.

Integration notes:
- OCFS2 writes valid but unmountable OCFS1 headers so OCFS1 can detect the partition and fail cleanly.
- This is structure definition only; no functions are declared.
