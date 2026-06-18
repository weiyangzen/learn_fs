# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_iconv/ntfs_iconv.c

This file declares NTFS support for the kernel iconv framework with `VFS_DECLARE_ICONV(ntfs)`. It includes kernel module, mount, and iconv headers.

There are no local functions beyond the macro expansion. The base NTFS code references `struct iconv_functions *ntfs_iconv` and uses it when `NTFS_MFLAG_KICONV` is set.

Research notes: this is glue code; charset conversion behavior lives in the generic iconv framework and in the NTFS conversion setup/use functions in `ntfs_subr.c`.
