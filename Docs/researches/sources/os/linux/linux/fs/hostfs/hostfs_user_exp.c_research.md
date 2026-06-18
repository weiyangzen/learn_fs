# File Research: sources/os/linux/linux/fs/hostfs/hostfs_user_exp.c

Purpose: Exports hostfs user-wrapper functions as GPL symbols for UML hostfs linkage.

Key content:
- `EXPORT_SYMBOL_GPL()` entries for hostfs stat, access, file I/O, directory I/O, create/remove/link/rename, setattr, readlink, mknod, and statfs wrappers.

Dependencies and integration:
- Includes `hostfs.h` and Linux module export support.
- Complements `hostfs_user.c` and the UML Makefile’s split build model.

Risk notes:
- Symbol export list must stay synchronized with declarations in `hostfs.h` and uses in `hostfs_kern.c`.
