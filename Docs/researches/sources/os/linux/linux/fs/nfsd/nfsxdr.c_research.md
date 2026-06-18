# File Research: sources/os/linux/linux/fs/nfsd/nfsxdr.c

## Summary
Implements NFSv2 XDR encoding and decoding helpers for NFSD procedure arguments and responses, including filehandles, attributes, names, read/write payloads, directory entries, statfs results, and response cleanup.

## Main Responsibilities
- Decodes NFSv2 filehandles, filenames, directory operation arguments, setattr attributes, read/write/create/rename/link/symlink/readdir arguments.
- Encodes NFSv2 status, filehandles, file attributes, attrstat, diropres, readlink, read, readdir, statfs, and simple status results.
- Converts Linux `kstat` data to NFSv2 `fattr`, including type mapping, ids in the request user namespace, symlink size cap, device encoding, fsid selection, and lease-aware mtime.
- Handles opaque payload pages for READ and READLINK replies.
- Provides release callbacks that drop response filehandles.

## Key Data Structures and Interfaces
- `nfs_ftypes[]` maps Linux inode mode file types to NFSv2 type constants.
- `svcxdr_decode_fhandle()` initializes `svc_fh` with a fixed `NFS_FHSIZE` handle.
- `svcxdr_decode_sattr()` translates NFSv2 sattr fields to Linux `iattr`.
- `svcxdr_encode_fattr()` serializes a `kstat` and filehandle/export context.
- `nfssvc_encode_entry()` is the directory callback used by `nfsd_readdir()`.
- `nfssvc_release_attrstat()`, `nfssvc_release_diropres()`, and `nfssvc_release_readres()` release response filehandles.

## Important Behavior
Filename decoding rejects zero-length names, names longer than `NFS_MAXNAMLEN`, embedded NULs, and slashes.

Setattr decoding treats `0xffffffff` as “do not set” and tolerates the Sun client `0xffff` mode sentinel. UID/GID conversion uses the request’s user namespace and only marks valid ids. A microsecond value of `1000000` on mtime triggers the old Sun convention for setting atime/mtime to current server time.

NFSv2 file attributes use a protocol-limited view: symlink size is capped at `NFS_MAXPATHLEN`, inode numbers and sizes are truncated to u32 fields, and fsid is derived from explicit export fsid, UUID xor, or encoded device depending on `fsid_source()`.

READ/READLINK encoders put data in pages and call `svc_encode_result_payload()` so the RPC layer accounts for payload placement. READDIR stores a cookie placeholder for each entry and patches the previous entry’s cookie when the next offset is known.

## Dependencies
Depends on NFSD VFS, XDR declarations, auth/user namespace helpers, lease timestamp helpers, XDR stream APIs, page-backed SunRPC buffers, and filehandle/export helpers.

## Risks and Subtleties
This file is protocol-ABI code. Compatibility quirks such as sentinel setattr values, `1000000` microseconds, u32 truncation, and NFSv2 cookie patching are intentional.

Directory encoding must roll back `dirlist.len` and clear `cookie_offset` when the buffer is too small; otherwise partial entries or bad cookies could be exposed to clients.
