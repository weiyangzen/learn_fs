# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/asm/uaccess.h

Empty compatibility header.

Key behavior:
- Contains no declarations, macros, includes, comments, or guards.

Filesystem/build relevance:
- Exists to satisfy Linux-style include paths that expect `asm/uaccess.h` while building the ReactOS ext2 filesystem driver.

Notable risks:
- Any source expecting Linux user-access helpers from this header must be adapted elsewhere in the ReactOS ext2 compatibility layer.
