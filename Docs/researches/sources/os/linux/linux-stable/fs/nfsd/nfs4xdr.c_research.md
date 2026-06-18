# File Research: sources/os/linux/linux-stable/fs/nfsd/nfs4xdr.c

## Summary
Implements server-side XDR decoding and encoding for Linux NFSD's NFSv4 protocol engine. This file translates compound request wire data into `nfsd4_*` operation structures, estimates reply sizes and duplicate-reply-cache behavior, encodes operation results, and handles the large NFSv4 file-attribute surface.

## Main APIs
- Request decode and cleanup: `nfs4svc_decode_compoundargs()`, `nfsd4_release_compoundargs()`.
- Reply encode: `nfs4svc_encode_compoundres()`, `nfsd4_encode_operation()`, `nfsd4_encode_replay()`.
- Attribute encoding helper: `nfsd4_encode_fattr_to_buf()`.
- Reply sizing: `nfsd4_check_resp_size()`.
- Supported attributes table: `nfsd_suppattrs`.

## Decode Path
The decoder starts with basic XDR helpers for counted opaques, path components, times, verifiers, bitmaps, stateids, clientids, owner strings, ACLs, security labels, and optional POSIX ACL structures. Temporary decoded data is held on `nfsd4_compoundargs.to_free` via `svcxdr_tmpalloc()`, with special handling for data that came from XDR scratch space.

`nfsd4_decode_fattr4()` is the central SETATTR/CREATE/OPEN attribute decoder. It rejects unsupported writeable attributes, decodes size, NFSv4 ACLs, mode, owner/group idmapping, access/modify times, security labels, NFSv4.2 delegated timestamps, `mode_umask`, and optional POSIX default/access ACLs. It validates that the encoded attrlist length matches the consumed bytes.

Per-operation decoders populate the `union nfsd4_op_u` payloads for NFSv4.0 operations, NFSv4.1 sessions/pNFS/stateid operations, NFSv4.2 copy/clone/allocate/seek/read-plus operations, and RFC 8276 xattr operations. Unsupported or configuration-disabled operations are mapped to `nfserr_notsupp`.

`nfsd4_decode_compound()` decodes the compound tag, minor version, operation count, operation opnums, and each operation body through `nfsd4_dec_ops`. It caps decoded operation count, allocates a larger op array when needed, rejects opnums outside the negotiated minor version, traces decode errors, computes a maximum reply reservation, chooses duplicate-reply-cache type for NFSv4.0, and disables splice reads when compound layout or reply size makes them unsafe.

## Encode Path
The encoder includes low-level writers for filehandles, NFS times, device numbers, change info, network addresses, pathname components, filesystem locations/referrals, NFSv4 ACL entries, security labels, POSIX ACLs, stateids, sessionids, and lock-denied records.

`nfsd4_encode_fattr4()` is the main attribute encoder. It makes a mutable copy of the requested bitmap, handles migrated/referral exports, checks delegation GETATTR conflicts for size/change/time attributes, gathers `vfs_getattr()` and `vfs_statfs()` data, composes a temporary filehandle when necessary, fetches NFSv4 ACLs, security labels, POSIX ACLs, and then emits the bitmap plus attribute value list by iterating `nfsd4_enc_fattr4_encode_ops`. It can encode core file metadata, fsid variants, lease time, ACL support, filesystem locations, quotas as no-ops, mounted-on fileid, pNFS layout attributes, clone block size, xattr support, open argument support, and POSIX ACL extension attributes.

Directory replies are encoded by `nfsd4_encode_dirlist4()` and `nfsd4_encode_entry4()`. They skip `.` and `..`, delay writing cookies until the next entry is known, optionally cross mountpoints, encode requested per-entry attributes, use `RDATTR_ERROR` when allowed, and enforce both `dircount` and `maxcount`.

Read replies have two data paths. `nfsd4_encode_splice_read()` uses splice-capable file operations for a single safe READ in a compound, while `nfsd4_encode_readv()` reads into the XDR page vector for ordinary or multiple reads. `READ_PLUS` currently emits a DATA segment when not already at EOF.

Operation result encoders are dispatched through `nfsd4_enc_ops`. They cover stateful responses such as OPEN delegations, LOCK denied data, CREATE/REMOVE/RENAME change info, SETCLIENTID, EXCHANGE_ID, CREATE_SESSION, SEQUENCE, TEST_STATEID, pNFS layout responses, server-to-server copy responses, offload status, seek, and xattr result bodies.

`nfsd4_encode_operation()` writes opnum and status, invokes operation-specific encoders when needed, commits or truncates XDR output on resource/reply-too-big errors, maps a few internal statuses to protocol statuses, saves replay data for NFSv4.0 stateowners, calls operation release hooks, and updates `rq_next_page`.

## NFSv4 Feature Coverage
- NFSv4.0: classic compound ops, OPEN/CLOSE/LOCK seqids, SETCLIENTID, RENEW, stateowner replay caching.
- NFSv4.1: sessions, SEQUENCE, channel attributes, EXCHANGE_ID state protection, backchannel security parameters, TEST/FREE_STATEID, directory delegations, pNFS when enabled.
- NFSv4.2: ALLOCATE/DEALLOCATE decode, COPY/COPY_NOTIFY/OFFLOAD_STATUS, READ_PLUS, SEEK, CLONE, delegated timestamp attrs, clone block size, extended attributes.
- Optional kernel features: `CONFIG_NFSD_PNFS`, `CONFIG_NFSD_V4_SECURITY_LABEL`, and `CONFIG_NFSD_V4_POSIX_ACLS`.

## Dependencies
Uses SunRPC `xdr_stream`, `xdr_buf`, svc request/reply reservation, VFS lookup/stat/statfs/readlink/read helpers, export lookup/access helpers, idmapper helpers, NFSv4 ACL conversion, LSM security labels, POSIX ACL APIs, NFSD file cache objects, NFSv4 state/delegation helpers, pNFS layout ops, and NFSD tracepoints.

Local headers include `idmap.h`, `acl.h`, `xdr4.h`, `vfs.h`, `state.h`, `cache.h`, `netns.h`, `pnfs.h`, `filecache.h`, `nfs4xdr_gen.h`, and `trace.h`.

## Risks
XDR buffer accounting is the primary invariant. Every decoder must consume exactly the wire representation and every encoder must reserve enough room, backpatch lengths/cookies/status fields correctly, and truncate partial results only where protocol-safe.

Attribute handling is subtle because the requested bitmap is modified based on export migration, filesystem capabilities, ACL support, security-label support, birthtime availability, and pNFS configuration. Incorrect filtering can produce protocol-inconsistent GETATTR/READDIR replies.

Read, READ_PLUS, READDIR, xattr, and pNFS replies interact with page-vector output, direct placement, payload marking, client maxcount limits, and session reply-size limits. Mistakes can cause short replies, `NFS4ERR_REP_TOO_BIG`, stale buffer contents, or non-idempotent operations after partial encoding.

NFSv4.0 replay behavior depends on caching only the correct already-encoded result body. Session-based NFSv4.1+ avoids the DRC but adds slot/cache-size constraints that have to be honored during encode.
