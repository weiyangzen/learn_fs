# File Research: sources/os/bsd/freebsd-src/sys/fs/nfsserver/nfs_nfsdsubs.c

This file provides NFS server support routines for protocol marshalling, file-handle parsing, error mapping, name parsing, export/security checks, and server-side data structure initialization. It is not an operation implementation file itself; it is the shared substrate used by NFS server RPC handlers.

Key responsibilities:
- Defines NFSv2 errno-to-wire-error mapping and per-operation NFSv3/NFSv4 allowed-error tables.
- Implements `nfsd_errmap()` to convert `nd->nd_repstat` into protocol-specific XDR error values, including NFSv4.1 behavior that accepts any valid NFS error after normalization.
- Handles mbuf-chain trimming in `nfsrv_adj()`, including `M_EXTPG` external-page mbufs where trailing pages must be unwired and freed.
- Builds weak cache consistency and post-operation attributes via `nfsrv_wcc()`, `nfsrv_postopattr()`, and `nfsrv_fillattr()`.
- Parses incoming file handles with `nfsrv_mtofh()`, including public file handles, NFSv4 named attributes, and pNFS data-server file handles.
- Parses NFS path components with `nfsrv_parsename()`, including public-filehandle canonical/native path handling, percent-decoding, slash rejection, NFSv4 `"."`/`"..”` rejection, and optional UTF-8 validation.
- Initializes NFS server hash tables and queues in `nfsd_init()`.
- Checks NFSv4 root export security in `nfsd_checkrootexp()`, including GSS, export security flags, and optional TLS/mTLS constraints.
- Extracts NFSv4 compound minor version and tag data in `nfsd_getminorvers()`.

Important globals and tunables:
- `enable_checkutf8` controls NFSv4 UTF-8 name validation.
- `enable_nobodycheck` and `enable_nogroupcheck` reject attempts to set owner/group to default nobody/nogroup identities.
- `nfs_v2pubfh`, `nfsrv_dontlisthead`, and `nfsrv_recalllisthead` are initialized here.
- VNET hash pointers are allocated for clients, locks, and sessions.

Implementation notes:
- Error maps are deliberately conservative. NFSv3/NFSv4 filtering returns a per-operation default error if the current error is not in the allowlist.
- `nfsrv_fixattr()` applies a subset of NFSv4 settable attributes after creation when allowed, temporarily elevating `cr_uid` to zero for group changes where the caller is a group member, then restoring it.
- ACL handling is conditional on `NFS4_ACL_EXTATTR_NAME`; unsupported ACL bits are cleared from the returned attribute bitmap.
- Referral attributes are encoded by `nfsrv_putreferralattr()`, which handles `fs_locations`, `rdattr_error`, type, fsid, and mounted-on-fileid.

Research-relevant risks:
- Many routines signal protocol-level errors by setting `nd->nd_repstat` while returning `0`; callers must distinguish RPC decode failure from NFS status failure.
- `nfsrv_fixattr()` mutates credentials transiently and must always restore `cr_uid`.
- `nfsrv_adj()` mutates and frees mbufs/pages; callers must treat the returned mbuf as the new tail.
- `nfsrv_parsename()` edits public lookup input bytes for native public paths and percent decoding, so buffer ownership and length accounting matter.
