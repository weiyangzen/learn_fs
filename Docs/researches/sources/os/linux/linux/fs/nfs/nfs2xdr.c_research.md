# File Research: sources/os/linux/linux/fs/nfs/nfs2xdr.c

## Purpose
Implements XDR encoding/decoding and the RPC procedure table for NFSv2.

## Encoding
Encodes v2 file handles, sattr, diropargs, readlink, read, write, create, remove, rename, link, symlink, and readdir arguments. It uses fixed-size v2 file handles and v2-specific 32-bit offset/count fields.

## Decoding
- Decodes status values through `decode_stat()` and maps protocol statuses to Linux errno.
- Decodes fattrs with user namespace uid/gid conversion, NFSv2 FIFO special handling, filesystem IDs, timestamps, and synthetic change attributes.
- Decodes read data into reply pages; NFSv2 has no explicit EOF flag, so EOF is set false in the read result.
- Decodes directory entries lazily from page cache in `nfs2_decode_dirent()`.
- Decodes statfs information into `struct nfs2_fsstat`.

## Edge Handling
- Rejects invalid uid/gid values.
- Checks path and filename lengths and terminates readlink path buffers.
- Detects short/cheating server read/path replies where reported length exceeds received data.
- Treats all NFSv2 writes as `NFS_FILE_SYNC`.

## RPC Table
Defines `nfs_procedures[]` for GETATTR, SETATTR, LOOKUP, READLINK, READ, WRITE, CREATE, REMOVE, RENAME, LINK, SYMLINK, MKDIR, RMDIR, READDIR, and STATFS, then exposes `nfs_version2`.

## Research Notes
This file is the NFSv2 wire-format boundary. The most important maintenance risk is preserving v2 quirks: fixed file handles, 32-bit sizes, no EOF-on-read flag, FIFO device encoding, and server-time timestamp convention.
