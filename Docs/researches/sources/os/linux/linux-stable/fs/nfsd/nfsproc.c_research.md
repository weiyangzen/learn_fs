# File Research: sources/os/linux/linux-stable/fs/nfsd/nfsproc.c

## Summary
Implements NFSv2 server procedures and registers the NFSv2 `svc_version` dispatch table.

## Main APIs
Handlers cover NULL, GETATTR, SETATTR, ROOT, LOOKUP, READLINK, READ, WRITECACHE, WRITE, CREATE, REMOVE, RENAME, LINK, SYMLINK, MKDIR, RMDIR, READDIR, and STATFS. `nfsd_version2` binds those handlers to XDR decoders/encoders and duplicate-reply-cache policies.

## Behavior
Each procedure translates NFSv2 arguments into shared NFSD VFS helpers, manages filehandle lifetimes, maps newer/internal NFSD errors down to NFSv2 status values, and chooses cache behavior for idempotent versus non-idempotent operations. CREATE handles NFSv2’s overloaded semantics for regular files, device nodes, FIFOs, existing files, and truncation behavior.

## State and Synchronization
Procedure-local state lives in RPC argument/response objects. Filehandle references are explicitly released after shared VFS helpers. READ and READDIR reserve response pages and payload space before encoding. Non-idempotent operations use reply-cache modes such as `RC_REPLBUFF` or `RC_REPLSTAT`.

## Risks
NFSv2 compatibility rules are subtle, especially SETATTR “touch” handling, CREATE type inference, and lossy error mapping. Missing `fh_put()` calls leak export/dentry references; premature release breaks response encoding. `nfserr_jukebox` paths set `RQ_DROPME` to force retry rather than sending an ordinary reply.
