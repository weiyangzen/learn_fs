# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_args.h

Read completely: 40 lines.

Defines the mount argument structure for NetBSD V7FS.

`struct v7fs_args` carries `fspec`, the block special device path to mount, and `endian`, the target filesystem byte order. The header only exposes this user/kernel mount ABI and uses a conventional include guard.

Risks and notes: no symbolic values for the `endian` field are defined here; callers must get those from the corresponding implementation or mount utility conventions.
