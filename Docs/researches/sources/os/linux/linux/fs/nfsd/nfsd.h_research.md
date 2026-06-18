# File Research: sources/os/linux/linux/fs/nfsd/nfsd.h

## Summary
Central NFSD internal header collecting service-wide constants, public prototypes, protocol version declarations, NFS status constants, NFSv4 attribute masks, and small helpers shared across the NFS server implementation.

## Main Responsibilities
- Defines supported NFS version limits, NFSv4 minor version limit, max compound operations, and service block-size limits.
- Declares global NFSD service state and entry points for service startup, shutdown, dispatch, thread accounting, version toggles, client directories, lockd, debugfs, and NFSv4 state lifecycle.
- Provides pre-XDR big-endian NFS error constants for NFSv2/v3/v4 paths.
- Defines supported and writable NFSv4 attribute bitmaps, including pNFS, security label, POSIX ACL, and exclusive-create variants.
- Supplies helpers for user namespace selection, NFSv4 client detection, netaddr formatting, bitmap subset checks, and attribute support checks.

## Key Data Structures and Interfaces
- `struct nfsd_genl_rqstp` is a stable snapshot used by netlink RPC status reporting.
- `struct nfsd_thread_local_info` stores per-thread compound/cache metadata.
- `struct nfsdfs_client` is the refcounted object attached to client debug filesystem entries.
- `enum vers_op` abstracts version mutation/testing through `nfsd_vers()` and `nfsd_minorversion()`.
- `nfsd_suppattrs[3][3]` and the `NFSD4_*_SUPPORTED_ATTRS_WORD*` masks define supported attribute sets by NFSv4 minor.

## Important Behavior
The header intentionally normalizes status handling by exposing big-endian constants such as `nfserr_stale`, `nfserr_wrongsec`, and NFSv4-specific errors. Internal-only sentinel statuses such as `nfserr_eof`, `nfserr_replay_me`, `nfserr_replay_cache`, and `nfserr_symlink_not_dir` are allocated outside assigned protocol errors before conversion to big-endian values.

NFSv4 attribute masks are split between supported, write-only, writable, and exclusive-create sets. Optional features alter the masks at compile time, so protocol handlers should test against these helpers instead of duplicating config logic.

When `CONFIG_NFSD_V4` or related options are disabled, this header provides no-op stubs for NFSv4 lifecycle, recovery, pNFS, callback, and state-revocation hooks, allowing non-v4 builds to share call sites.

## Dependencies
Includes core NFS protocol headers, SunRPC service and transport APIs, UAPI NFSD debug definitions, export definitions, per-net NFSD state, and stats declarations.

## Risks and Subtleties
This header is a broad coupling point. Changes to error constants, version limits, or attribute masks affect many protocol paths and must remain consistent with XDR encoding, protocol specifications, and optional config stubs.

`nfsd_user_namespace()` derives the namespace from the transport credential when present; callers using request credentials for id translation should preserve that behavior for container/user-namespace correctness.
