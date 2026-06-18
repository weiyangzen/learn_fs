# File Research: sources/os/linux/linux-stable/fs/nfsd/xdr3.h

Purpose: defines NFSD NFSv3 XDR argument/result structures, request storage, procedure decoder/encoder prototypes, readdir entry encoders, release hooks, and NFSv3 ACL helper declarations.

Key structures and state:
- Argument structs cover setattr with guard time, dirop, access, read/write with 64-bit offsets, create/mknod, rename, link, symlink, readdir with verifier, commit, getacl, and setacl.
- Result structs cover attrstat, dirop, access, readlink, read, write with verifier, rename/link WCC-style filehandles, readdir/readdirplus scratch, fsstat, fsinfo, pathconf, commit, and getacl.
- `struct nfsd3_readdirres` contains the response filehandle, verifier, XDR stream, dirlist buffer, scratch filehandle for readdirplus, common readdir context, cookie offset, and request pointer.
- `struct nfsd3_fhandle_pair` is a dummy release type for procedures that need two filehandles released.
- `union nfsd3_xdrstore` sizes the per-request argument/result buffer via `NFS3_SVC_XDRSIZE`.

Major logic:
- Declares NFSv3 argument decoders for core file, directory, read/write, create, mknod, rename/link/symlink, readdir/readdirplus, and commit operations.
- Declares result encoders for getattr, WCC status, lookup, access, readlink, read, write, create, rename, link, readdir, fsstat, fsinfo, pathconf, and commit.
- Declares release hooks for one or two filehandles.
- Declares cookie and entry encoders for plain readdir and readdirplus.
- Provides NFSv3 ACL helper prototypes for filehandle decode, status encode, and post-op attribute encode.

Concurrency and lifetime:
- Filehandle-containing results and ACL objects are released by procedure release hooks after SunRPC encoding.
- Readdirplus uses a scratch filehandle that must be managed while encoding individual entries.

Important dependencies:
- Extends `xdr.h` and shares lower-level NFSv2/NFSD types.
- Used by `nfs3proc.c`, `nfs3xdr.c`, ACL code, and VFS readdir callbacks.

Risk/edge cases:
- Guarded setattr depends on preserving decoded guard timestamps exactly.
- Readdir verifiers and cookie offsets are protocol-visible and must stay consistent with encoder behavior.
- ACL result structures carry POSIX ACL pointers whose lifetime must be released exactly once.
