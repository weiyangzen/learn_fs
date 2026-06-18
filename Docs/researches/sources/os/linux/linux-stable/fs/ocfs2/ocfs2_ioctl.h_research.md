# File Research: sources/os/linux/linux-stable/fs/ocfs2/ocfs2_ioctl.h

Purpose: defines OCFS2 ioctl UAPI structures, command numbers, request codes, and flags for space reservation, online resize/group add, reflink, filesystem information queries, and extent movement.

Read coverage: complete file read, 224 lines.

Key UAPI groups:
- `struct ocfs2_space_resv` and `OCFS2_IOC_*SP*` commands mirror XFS-style space reservation/free allocation ioctl layouts; comments state `ALLOCSP*` and `FREESP*` are listed for completeness but unsupported.
- `struct ocfs2_new_group_input` with `OCFS2_IOC_GROUP_EXTEND`, `OCFS2_IOC_GROUP_ADD`, and `OCFS2_IOC_GROUP_ADD64` supports online resize/group descriptor additions.
- `struct reflink_arguments` and `OCFS2_IOC_REFLINK` pass old path, new path, and preserve flag for legacy OCFS2 reflink operations.
- `struct ocfs2_info` plus `struct ocfs2_info_request` and typed payloads implement batched `OCFS2_IOC_INFO` requests for cluster size, block size, max slots, label, UUID, feature bits, journal size, free inode stats, and free fragmentation stats.
- `struct ocfs2_move_extents` and `OCFS2_IOC_MOVE_EXT` define manual/automatic extent movement and defragmentation requests.

Constants and flags:
- `OCFS2_INFO_MAX_REQUEST` caps batched info requests at 50.
- `OCFS2_INFO_MAGIC` identifies valid info request objects.
- `OCFS2_INFO_FL_NON_COHERENT` asks the kernel to avoid cluster-coherent locking if possible; `OCFS2_INFO_FL_FILLED` and `OCFS2_INFO_FL_ERROR` are kernel-returned status flags.
- Move-extents flags include automatic defrag, partial defrag, and completion indication.

Dependencies:
- References `OCFS2_VOL_UUID_LEN`, `OCFS2_MAX_VOL_LABEL_LEN`, and `OCFS2_MAX_SLOTS` from OCFS2 disk format definitions.
- Consumed by OCFS2 ioctl dispatch in `ioctl.c` and by userspace tools issuing these ioctls.

Risk and edge cases:
- Pointer fields are encoded as `__u64` for userspace ABI stability and compat handling.
- Packed label/UUID info structures avoid unintended padding changes.
- Request `ir_size` and `ir_code` validation in the implementation depends on these exact structure sizes and enum values.
