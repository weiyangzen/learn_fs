# File Research: sources/teaching/minix/minix/servers/vfs/file.h

Header defining VFS filp table entries.

`struct filp` represents an open file description shared by one or more file descriptors.

Main fields:
- `filp_mode`: read/write bits or `FILP_CLOSED`.
- `filp_flags`: open/fcntl flags.
- `filp_count`: number of descriptors sharing the filp.
- `filp_vno`: vnode pointer.
- `filp_pos`: file offset.
- `filp_lock`: mutex for exclusive filp access.
- `filp_softlock`: tracks cases where the vnode is already locked by this thread.
- `filp_ioctl_fp`: marks block-device ioctl ownership for deadlock avoidance.
- select state fields for generic select and fd-type-specific select.

Defines:
- Global `filp[NR_FILPS]`.
- `FILP_CLOSED`.
- Select flags `FSF_UPDATE`, `FSF_BUSY`, `FSF_RD_BLOCK`, `FSF_WR_BLOCK`, `FSF_ERR_BLOCK`, `FSF_BLOCKED`.
