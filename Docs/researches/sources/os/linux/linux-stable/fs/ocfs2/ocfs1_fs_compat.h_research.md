# File Research: sources/os/linux/linux-stable/fs/ocfs2/ocfs1_fs_compat.h

Purpose: defines the OCFS1-compatible volume header and label structures that OCFS2 writes into the first two sectors so old OCFS1 code detects the partition and fails cleanly instead of mis-mounting it.

Read coverage: complete file read, 94 lines.

Key structures and constants:
- Defines OCFS1 string limits for volume signature, mount point, volume id, label, and cluster name.
- Defines OCFS1 compatibility version `2.0` and signature `"OracleCFS"`.
- `struct ocfs1_vol_disk_hdr` models the OCFS1 sector-0 volume header, including version, signature, mount point, serial/device size, bitmap/public/vote/root offsets, data/root sizes, cluster/node counts, node config offsets, protection bits, and exclusive mount field.
- `struct ocfs1_disk_lock` models the OCFS1 disk lock embedded in the volume label, with explicit padding for historical alignment.
- `struct ocfs1_vol_label` models the sector-1 volume label with disk lock, label, volume id, and cluster name fields.

Dependencies:
- Uses fixed-width Linux integer types only; this header is a disk-layout compatibility contract, not active OCFS2 runtime logic.

Risk and edge cases:
- Structure offsets are annotated and effectively ABI-sensitive. Padding or field-size changes would alter the compatibility sectors.
- These headers are intentionally valid enough for OCFS1 recognition but describe an unmountable OCFS1 volume.
