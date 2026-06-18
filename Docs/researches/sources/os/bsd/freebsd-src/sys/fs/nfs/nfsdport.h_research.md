# File Research: sources/os/bsd/freebsd-src/sys/fs/nfs/nfsdport.h

This FreeBSD port header adapts generic NFS server code to FreeBSD vnode, mount, credential, export, namei, file, and debug conventions.

Key behavior:
- Defines `NFSVNO_*` macros for initializing, setting, testing, and unsetting `nfsvattr` fields using FreeBSD `vattr` storage and `VNOVAL`.
- Defines `struct nfsexstuff`, a catch-all export result used by file-handle-to-vnode and export checks. It carries export flags plus accepted security flavors.
- Defines `NFSEXITCODE()` and `NFSEXITCODE2()` as no-ops on FreeBSD; comments describe a non-upstream EXITCODE tracing facility used elsewhere.
- Defines export flag helpers for read-only, anon, strict-access, v4-only, and TLS/certificate export modes.
- Defines `NFSVNO_SETEXRDONLY()` to mark an export record read-only.
- Defines `NFSVNO_CMPFH()` for comparing FreeBSD file handles by fsid and fid.
- Defines `NFSLOCKHASH()` for selecting an NFS lock hash bucket from a file handle.
- Defines file pointer accessor macros for vnode, credential, and flags.
- Defines `NFSNAMEICNDSET()` to populate FreeBSD namei component fields.
- Defines FreeBSD path length type, server file-handle min/max sizes, and `NFSD_DEBUG()` gated by `nfsd_debuglevel`.

Important interactions:
- Used by server-side code that is shared with other platform ports but needs FreeBSD-specific vnode/export/namei behavior.
- `nfsexstuff` is passed through server access, lookup, file-handle, and export-check paths.
- `NFSEXITCODE*` calls in common code compile away on FreeBSD.

Edge cases:
- The file-handle size macros are fixed to `sizeof(fhandle_t)`, matching FreeBSD’s server-side native file handle.
- The attribute macros assume `struct nfsvattr` embeds/aliases fields using the `na_` naming convention.
