# File Research: sources/os/linux/linux/fs/ocfs2/move_extents.h

`move_extents.h` declares the ioctl entry point:

- `ocfs2_ioctl_move_extents(struct file *filp, void __user *argp)`

It connects `ioctl.c` command dispatch to the extent movement/defragmentation implementation in `move_extents.c`.
