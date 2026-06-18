# File Research: sources/os/linux/linux-stable/fs/nfsd/nfsxdr.c

## Summary
NFSv2 XDR decoder/encoder implementation for NFSD.

## Main APIs
- Basic helpers: `svcxdr_encode_stat()`, `svcxdr_decode_fhandle()`, `svcxdr_encode_fattr()`.
- Decoders: fhandle, sattr, diropargs, read, write, create, rename, link, symlink, readdir.
- Encoders: stat, attrstat, diropres, readlink, read, readdir, statfs, directory entries.
- Release hooks: `nfssvc_release_attrstat()`, `nfssvc_release_diropres()`, `nfssvc_release_readres()`.

## Behavior
Decoding validates fixed NFSv2 filehandle sizes, component names, attribute sentinel values, user/group ids in the request namespace, read/write offsets/counts, and symlink payload placement. Encoding emits NFSv2 file attributes, including type mapping, uid/gid munging, device/fsid/fileid values, lease-adjusted mtime, opaque payload pages, and READDIR cookie backpatching.

## State and Synchronization
The code works against `xdr_stream`, RPC request pages, and `svc_fh` response objects. READ/READLINK/READDIR encoders attach page-backed payloads and mark result payload ranges for RPC accounting. Release hooks drop response filehandles after encoding.

## Risks
All buffer reservations are manual, so encode paths must fail cleanly before overrunning the response stream. Filename validation rejects embedded NUL and slash; relaxing that would affect VFS path safety. READDIR stores a cookie offset for later backpatching, so failed entry encoding must restore the previous buffer length.
