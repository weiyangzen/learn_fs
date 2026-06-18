# File Research: sources/os/linux/linux-stable/fs/smb/client/smb2glob.h

## Purpose
Defines small SMB2-global constants and structures shared by SMB2 client implementation files.

## Main Contents
- `enum smb2_compound_ops` enumerates operation IDs consumed by `smb2inode.c:smb2_compound_op()`.
- Compound operation IDs cover delete, set/query info, query directory, mkdir, rename, hardlink, EOF set, unlink, POSIX query info, reparse set/get, WSL EA query, and open-query.
- Chained request flags define start/end/related request state for compound/chained SMB2 operations.
- `struct status_to_posix_error` stores NT status code, Linux errno, and printable status string for SMB2 error mapping.

## Role in This Group
This header is the shared contract between:
- `smb2inode.c`, which dispatches `enum smb2_compound_ops`.
- `smb2maperror.c`, which uses `struct status_to_posix_error`.
- KUnit map-error tests that inspect the exported mapping table shape.
