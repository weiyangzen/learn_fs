# File Research: sources/os/linux/linux/fs/ocfs2/ocfs2_ioctl.h

Role: Defines OCFS2 userspace ioctl ABI structures and command numbers.

Key contents:
- `struct ocfs2_space_resv`: XFS-compatible space reservation argument layout. `ALLOCSP*` and `FREESP*` commands are declared for completeness but documented as unsupported.
- Space ioctls:
  - `OCFS2_IOC_ALLOCSP`
  - `OCFS2_IOC_FREESP`
  - `OCFS2_IOC_RESVSP`
  - `OCFS2_IOC_UNRESVSP`
  - 64-bit variants for alloc/free/reserve/unreserve
- Online resize input:
  - `struct ocfs2_new_group_input`
  - `OCFS2_IOC_GROUP_EXTEND`
  - `OCFS2_IOC_GROUP_ADD`
  - `OCFS2_IOC_GROUP_ADD64`
- Reflink ABI:
  - `struct reflink_arguments`
  - `OCFS2_IOC_REFLINK`
- Batched info ABI:
  - `struct ocfs2_info`
  - base `struct ocfs2_info_request`
  - typed requests for cluster size, block size, max slots, label, UUID, feature masks, journal size, free inode stats, and free-fragmentation stats
  - `enum ocfs2_info_type`
  - request flags for non-coherent hint, filled response, and per-request error
  - `OCFS2_IOC_INFO`
- Extent movement/defragment ABI:
  - `struct ocfs2_move_extents`
  - flags for auto defrag, partial defrag, and completion
  - `OCFS2_IOC_MOVE_EXT`

Design notes:
- Structures use fixed-width integer types and reserved fields to preserve ABI compatibility.
- The info ioctl is explicitly designed as small request records to preserve backward and forward compatibility.
- This header is pulled into `ocfs2.h`, so kernel code can share exact ioctl ABI definitions with userspace-facing handlers.
