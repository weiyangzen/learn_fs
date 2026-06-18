# File Research: sources/os/linux/linux/io_uring/xattr.h

Header for io_uring xattr operations.

Key responsibilities:
- Declares common xattr cleanup.
- Declares prep and issue functions for file and path variants of setxattr and getxattr.

Important invariant:
- All xattr prep paths that allocate/import state must arrange cleanup through `io_xattr_cleanup()`.
