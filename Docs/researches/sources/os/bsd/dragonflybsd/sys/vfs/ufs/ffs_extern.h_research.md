# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ffs_extern.h

Public internal FFS function and sysctl declaration header.

Key responsibilities:
- Defines FFS sysctl IDs and the `FFS_NAMES` table entries for `doreallocblks` and `doasyncfree`.
- Forward-declares kernel types needed by FFS APIs.
- Declares allocation, block mapping, mount, sync, statfs, truncate, update, vnode allocation/free/get, file-handle, and bitmap helper functions implemented across FFS source files.
- Declares soft updates entry points used by FFS code for inode block updates, mount/flush handling, allocation dependencies, freeblock setup, metadata sync, and freefile handling.

Dependencies:
- Depends on UFS disk address and logical block typedefs being available from included context.
- Shared by FFS allocation, inode, mount, vnode, and soft updates implementation files.

Notable risks:
- Function prototypes are cross-file kernel contracts; signature drift causes build or ABI-like internal breakage.
- Soft updates declarations are tightly coupled to metadata update ordering in allocation and truncate code.
- Sysctl ID values must stay consistent with existing kernel/user expectations.
