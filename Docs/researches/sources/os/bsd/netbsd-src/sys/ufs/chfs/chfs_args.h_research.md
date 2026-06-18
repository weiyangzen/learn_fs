# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_args.h

Read completely: 44 lines.

Mount argument header for CHFS.

Core definitions:
- `CHFS_ARGS_VERSION` is 1.
- `struct chfs_args` carries `fspec` and `fl_index`, the index of the flash device in the flash layer.

Risks and notes:
- This is a mount ABI structure; changes require compatibility handling.
