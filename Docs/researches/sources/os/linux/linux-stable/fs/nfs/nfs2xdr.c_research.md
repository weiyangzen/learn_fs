# File Research: sources/os/linux/linux-stable/fs/nfs/nfs2xdr.c

## Purpose
Implements NFSv2 XDR encoding/decoding and exports the NFSv2 RPC procedure table.

## Basic Type Handling
- Uses RFC 1094 layout sizes for handles, attributes, paths, filenames, data, and result unions.
- Translates RPC credentials to user namespace via `rpc_rqst_userns()`.
- `decode_nfsdata()` reads page-backed opaque read data and clamps cheating servers that report more data than received.
- `decode_stat()` reads NFS status and maps nonzero values later through `nfs_stat_to_errno()`.
- `xdr_decode_ftype()` maps v2 file type values and sanitizes invalid types.
- `encode_fhandle()` / `decode_fhandle()` handle fixed `NFS2_FHSIZE` file handles.
- Time helpers encode/decode v2 timeval, including the Sun convention for "set to current server time" using usec `1000000`.

## Attribute Handling
- `decode_fattr()` fills `nfs_fattr` from v2 `fattr`, including mode, nlink, uid/gid translation, size, blocksize, rdev, blocks, fsid, fileid, timestamps, and synthetic change attribute.
- Handles the v2 FIFO convention where `NFCHR` plus `NFS2_FIFO_DEV` becomes `S_IFIFO`.
- `encode_sattr()` writes `sattr`, using `NFS2_SATTR_NOT_SET` for unchanged fields.

## Argument Encoders
- File handle: `nfs2_xdr_enc_fhandle()`.
- Setattr: `nfs2_xdr_enc_sattrargs()`.
- Lookup/remove/rmdir style directory args: `nfs2_xdr_enc_diropargs()` and `nfs2_xdr_enc_removeargs()`.
- Readlink/read: prepare reply pages and mark read buffers.
- Write: encodes offset/count and writes pages to XDR buffer.
- Create/mkdir: dir args plus attributes.
- Rename, link, symlink, readdir: protocol-specific encoders.

## Result Decoders
- `nfs2_xdr_dec_stat()`, `nfs2_xdr_dec_attrstat()`, `nfs2_xdr_dec_diropres()`.
- `nfs2_xdr_dec_readlinkres()` decodes path into page-backed buffer and terminates string.
- `nfs2_xdr_dec_readres()` decodes status, fattr, and read data.
- `nfs2_xdr_dec_writeres()` treats all v2 writes as `NFS_FILE_SYNC`.
- `nfs2_xdr_dec_readdirres()` stores raw directory bytes into page cache.
- `nfs2_xdr_dec_statfsres()` decodes transfer size, block size, blocks, free, and available blocks.

## Directory Entry Decoding
- `nfs2_decode_dirent()` decodes cached readdir entries on later `getdents()` processing.
- Handles EOF markers, fileid, inline filename, 32-bit cookie, and sets `DT_UNKNOWN`.

## RPC Table
- `nfs_procedures[]` covers GETATTR, SETATTR, LOOKUP, READLINK, READ, WRITE, CREATE, REMOVE, RENAME, LINK, SYMLINK, MKDIR, RMDIR, READDIR, and STATFS.
- `nfs_version2` exports version number 2, procedure table, and per-procedure counters.

## Research Notes
The file is strictly v2 protocol translation. Notable compatibility behavior includes UID/GID namespace translation, FIFO special-case handling, v2 synchronous write semantics, and defensive handling of oversized or inconsistent server replies.
