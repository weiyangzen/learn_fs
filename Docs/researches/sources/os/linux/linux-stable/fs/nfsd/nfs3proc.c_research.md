# File Research: sources/os/linux/linux-stable/fs/nfsd/nfs3proc.c

## Summary
NFSv3 server procedure implementation. It adapts decoded RPC arguments to NFSD VFS helpers and wires all NFSv3 procedures into the SunRPC `svc_version`.

## Main APIs
Implements `GETATTR`, `SETATTR`, `LOOKUP`, `ACCESS`, `READLINK`, `READ`, `WRITE`, `CREATE`, `MKDIR`, `SYMLINK`, `MKNOD`, `REMOVE`, `RMDIR`, `RENAME`, `LINK`, `READDIR`, `READDIRPLUS`, `FSSTAT`, `FSINFO`, `PATHCONF`, and `COMMIT`.

## Behavior
Most procedures copy input filehandles into response handles, call a VFS helper, map internal errors through `nfsd3_map_status()`, and return `rpc_success`. `CREATE` handles unchecked, guarded, and exclusive semantics, including verifier-derived atime/mtime. Directory reads allocate reply pages and patch cookies via XDR helpers. `COMMIT` acquires a GC-backed write file from the filecache before flushing.

## State and Protocol Table
`nfsd_procedures3` defines decoder, encoder, release callback, argument/result sizes, reply cache policy, estimated XDR result size, and procedure name for all 22 NFSv3 operations.

## Risks
Read/write counts are clamped to service payload and `OFFSET_MAX`. Non-idempotent operations use reply caching; changing cache type can affect client replay semantics. READDIRPLUS depends on export flags and per-entry filehandle composition.
