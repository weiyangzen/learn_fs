# File Research: sources/os/linux/linux/fs/nfsd/nfsfh.c

## Summary
Implements NFSD filehandle verification, composition, release, weak cache consistency attribute capture, optional signed filehandle MACs, and NFSv4 change attribute generation.

## Main Responsibilities
- Decodes on-the-wire filehandles into exports and dentries via export cache lookup and filesystem `export_operations`.
- Performs export, subtree, secure-port, xprtsec, security flavor, type, pseudo-root, and VFS permission checks.
- Composes filehandles for replies using export fsid policy, filesystem file identifiers, reference filehandles, UUID/device/fsid encodings, and optional SipHash MAC signing.
- Maintains `svc_fh` lifetime, including dentry/export references, mount write access, and pre/post operation attributes.
- Generates NFSv4 change attributes from `STATX_CHANGE_COOKIE` and ctime fallback/mitigation.

## Key Data Structures and Interfaces
- `nfsd_set_fh_dentry()` maps `knfsd_fh` content to `fh_export` and `fh_dentry`.
- `__fh_verify()` is the core verifier behind RPC `fh_verify()` and non-RPC `fh_verify_local()`.
- `fh_compose()` builds a new `svc_fh` for a dentry/export pair.
- `fh_update()` finalizes filehandles after create operations that started from negative dentries.
- `fh_fill_pre_attrs()`, `fh_fill_post_attrs()`, and `fh_fill_both_attrs()` support weak cache consistency and NFSv4 change info.
- `fh_append_mac()` and `fh_verify_mac()` implement optional `NFSEXP_SIGN_FH` protection.

## Important Behavior
Subtree checking uses `nfsd_acceptable()` to walk ancestors up to the export root and ensure execute permission on each parent. For `NFSEXP_NOSUBTREECHECK`, lookup temporarily raises effective capabilities so `exportfs_decode_fh_raw()` can reconnect dentries through inaccessible parent paths.

Filehandle verification first locates the export by fsid, then decodes the file id unless the handle identifies the export root. NFSv4 pseudo-root exports expose only the pseudoroot object and traversable directories/symlinks, returning stale for unrelated objects.

Security checks are layered: secure source port, export user credential setup, xprtsec policy, GSS flavor policy with explicit bypass cases, then filesystem permission checks. LOCALIO calls pass `rqstp == NULL` and intentionally skip transport-security and flavor checks because access was already affirmed over NFS.

Composition chooses fsid encoding from a reference filehandle when compatible, otherwise from explicit export fsid, export UUID, or device number. It handles root filehandles specially with `FILEID_ROOT` and signs non-root filehandles when export policy requires it.

Weak cache consistency is disabled for exports/filesystems that advertise no WCC support. NFSv4 filehandles request btime and change-cookie attrs, while regular files with non-monotonic change cookies are mixed with ctime to avoid reuse after unclean shutdown.

## Dependencies
Uses Linux `exportfs`, VFS path and permission APIs, mount write accounting, NFSD export/auth/vfs helpers, tracepoints, crypto `siphash` and constant-time compare, kstat/statx, and per-net NFSD state.

## Risks and Subtleties
This is a security-critical path. Skipping `fh_verify()` or reusing verified dentries without rechecking permissions can miss changed export options, security flavor requirements, mount crossings, or credential changes.

Signed filehandles depend on a configured per-net `fh_key`; missing key or insufficient handle space degrades composition/verification and is rate-limited in logs. Any change to filehandle size accounting must preserve MAC word subtraction before `exportfs_decode_fh_raw()`.

Reference and cleanup discipline is strict: successful verification owns dentry/export references, `fh_put()` drops them and mount write access, and create paths must call `fh_update()` when a dentry becomes positive after initial composition.
