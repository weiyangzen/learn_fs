# File Research: sources/os/linux/linux-stable/fs/nfsd/xdr.h

Purpose: defines the server-side XDR argument/result storage types and encode/decode entry points for NFSv2 NFSD procedures.

Key structures and state:
- Argument structs wrap filehandles and decoded parameters for setattr, dirop, read, write, create, rename, link, symlink, and readdir.
- Result structs hold status, filehandles, kstats, pages, read counts, statfs data, and readdir encoding scratch state.
- `struct nfsd_readdirres` owns an XDR stream, dirlist buffer, common readdir context, and cookie offset used while encoding directory entries.
- `union nfsd_xdrstore` is the per-request storage union sized by `NFS2_SVC_XDRSIZE`.

Major logic:
- Declares per-procedure NFSv2 decoders for fhandle, setattr, dirop, read, write, create, rename, link, symlink, and readdir args.
- Declares result encoders for status, attrstat, dirop, readlink, read, statfs, and readdir.
- Declares readdir cookie/entry encoders and release hooks for responses that hold filehandles or pages.
- Provides helper encode/decode functions for NFSv2 ACL code: filehandle, status, and file attributes.

Concurrency and lifetime:
- The header defines storage ownership used by SunRPC service dispatch; release hooks are responsible for dropping references acquired during procedure handling.
- Read and readlink results carry page pointers that must be released by the corresponding service release path.

Important dependencies:
- Includes VFS, NFSD core, and filehandle definitions.
- Implemented by NFSv2 XDR/procedure code and consumed by the NFSD RPC version table.

Risk/edge cases:
- NFSv2 uses 32-bit offsets/counts in these structures, so callers must preserve protocol truncation/limit behavior.
- `NFS2_SVC_XDRSIZE` must remain large enough for the largest union member.
