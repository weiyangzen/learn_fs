# File Research: sources/os/linux/linux/fs/nfs/nfs3xdr.c

## Purpose
Implements XDR encoding/decoding and RPC procedure tables for NFSv3 and optional NFSv3 ACL side protocol.

## Encoding
Encodes NFSv3 primitive types, file handles, sattrs, diropargs, getattr/setattr, lookup, access, readlink, read, write, create, mkdir, symlink, mknod, remove, rename, link, readdir, readdirplus, commit, and optional ACL GETACL/SETACL arguments.

## Decoding
- Decodes protocol statuses and maps them to errno.
- Decodes fattrs with user namespace uid/gid conversion, device numbers, fsid/fileid, timestamps, and synthetic change attributes.
- Decodes post-op attrs and weak-cache-consistency data.
- Decodes read/write results, including opaque length matching, EOF, stable write verifier, op status, and server-cheating checks.
- Decodes create, remove, rename, link, readdir/readdirplus, fsstat, fsinfo, pathconf, and commit results.
- `nfs3_decode_dirent()` lazily decodes cached directory entries and handles READDIRPLUS fattrs/file handles, `mounted_on_fileid`, and `d_type`.
- ACL decoders validate returned ACL masks and decode access/default ACL payloads.

## Notable Behavior
- Rejects zero or oversized v3 file handles.
- `decode_pathconf3resok()` stores `max_link`, `max_namelen`, `case_insensitive`, and `case_preserving`.
- READDIR replies are read into page cache with actual entry decoding deferred to getdents-time.
- FSINFO clears v4-only lease/change/xattr fields.
- COMMIT sets verifier committed mode to `NFS_FILE_SYNC` on success.

## RPC Tables
Defines `nfs3_procedures[]` for all core NFSv3 procedures and exposes `nfs_version3`. Under `CONFIG_NFS_V3_ACL`, defines `nfs3_acl_procedures[]` and `nfsacl_version3`.

## Research Notes
This is the NFSv3 wire-format boundary. The most sensitive areas are XDR length accounting, uid/gid namespace conversion, WCC/post-op attr preservation, READ/READDIR page handling, pathconf case flags, and ACL page-buffer encoding/decoding.
