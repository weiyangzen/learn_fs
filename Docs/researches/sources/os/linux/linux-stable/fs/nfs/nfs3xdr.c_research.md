# File Research: sources/os/linux/linux-stable/fs/nfs/nfs3xdr.c

## Purpose
Implements NFSv3 XDR encoding/decoding, NFSv3 directory-entry decoding from cached readdir pages, optional NFSACL v3 XDR, and exports the NFSv3 RPC version/procedure tables.

## Sizing and Primitive Types
- Defines request/reply XDR word-size constants for NFSv3 operations and ACL operations.
- Maps NFSv3 file types to Linux `S_IFMT` bits using `nfs_type2fmt`.
- Provides user namespace helpers for UID/GID translation.
- Encodes/decodes primitives:
  - uint32/uint64
  - fileid3, filename3, nfspath3
  - cookie3 and cookie verifier
  - create/write verifiers
  - size3
  - nfsstat3
  - ftype3
  - specdata3
  - variable-length `nfs_fh3`
  - nfstime3

## Attribute and WCC Handling
- `encode_sattr3()` encodes optional mode/uid/gid/size/atime/mtime fields using NFSv3 discriminated unions.
- `decode_fattr3()` fills `nfs_fattr`, including mode/type, link count, namespace-translated uid/gid, size, used blocks, rdev, fsid, fileid, timestamps, change attribute, and valid flags.
- `decode_post_op_attr()` handles optional post-op attrs.
- `decode_wcc_attr()`, `decode_pre_op_attr()`, and `decode_wcc_data()` decode weak cache consistency data.
- `decode_post_op_fh3()` handles optional returned file handles and zeroes the handle when absent.

## Argument Encoders
- GETATTR, SETATTR with optional ctime guard, LOOKUP, ACCESS.
- READLINK and READ prepare page-backed reply buffers.
- WRITE writes page data and marks XDR buffer as write data.
- CREATE encodes unchecked, guarded, or exclusive create forms.
- MKDIR, SYMLINK, MKNOD, REMOVE, RENAME, LINK.
- READDIR and READDIRPLUS encode cookies/verifiers and prepare page-backed directory replies.
- COMMIT encodes file handle, offset, and count.
- Optional ACL encoders:
  - GETACL prepares sparse reply pages when ACL data is requested.
  - SETACL writes ACL payload inline or through pages and uses `nfsacl_encode()`.

## Result Decoders
- GETATTR, SETATTR, LOOKUP, ACCESS, READLINK.
- READ:
  - `decode_read3resok()` validates count against opaque length, reads pages, handles cheating server counts, and sets EOF/count.
  - `nfs3_xdr_dec_read3res()` records op status and reply header length.
- WRITE:
  - Decodes WCC data, count, stable commit level, and write verifier.
  - Rejects invalid `stable_how`.
- CREATE:
  - Decodes optional returned file handle and attrs.
  - If server omits file handle, invalidates fattr to force a later LOOKUP.
- REMOVE, RENAME, LINK decode relevant WCC/post-op attrs.
- READDIR:
  - Stores raw directory bytes in page cache for later decoding.
  - Decodes directory attrs and cookie verifier.
- FSSTAT, FSINFO, PATHCONF, COMMIT:
  - Fill stat, server I/O limits, name/link limits, max file size, time delta, and commit verifier information.
- Optional ACL decoders:
  - GETACL decodes fattr, mask, access ACL, and default ACL.
  - SETACL decodes post-op attrs on success.

## Cached Directory Entry Decoding
- `nfs3_decode_dirent()`
  - Decodes raw cached READDIR/READDIRPLUS entries during `getdents()` processing.
  - Handles EOF marker via `-EBADCOOKIE`.
  - Decodes fileid, filename, cookie.
  - For READDIRPLUS, decodes post-op attrs and optional file handle.
  - Sets `d_type` from decoded mode when attrs are available.
  - Handles mounted-on-fileid when fattr fileid differs from entry fileid.

## RPC Tables
- `nfs3_procedures[]` covers GETATTR, SETATTR, LOOKUP, ACCESS, READLINK, READ, WRITE, CREATE, MKDIR, SYMLINK, MKNOD, REMOVE, RMDIR, RENAME, LINK, READDIR, READDIRPLUS, FSSTAT, FSINFO, PATHCONF, and COMMIT.
- `nfs_version3` exports NFS protocol version 3 and counters.
- Under `CONFIG_NFS_V3_ACL`, `nfs3_acl_procedures[]` and `nfsacl_version3` export GETACL/SETACL.

## Research Notes
This file is the authoritative NFSv3 wire-format implementation. Key correctness points are variable file-handle bounds, UID/GID namespace validation, weak cache consistency preservation, page-backed read/readdir data handling, verifier validation, and ACL page/inline encoding.
