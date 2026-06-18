# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_subs.c

This file contains shared NFS support routines for client and server code: global constants, protocol maps, initialization, attribute caching, server name/file-handle helpers, directory cookies, commit cleanup, error mapping, and credential helpers.

Global initialization:
- Defines pre-XDR-converted constants such as `rpc_reply`, `rpc_call`, `rpc_auth_unix`, `rpc_auth_kerb`, `nfs_prog`, `nfs_true`, `nfs_false`, and `nfs_xdrneg1`.
- `nfs_init()` initializes callouts, mount type, NFS node hash, server cache/data structures, timer interval, async BIO limits, timer callout, and installs `sys_nfssvc` into the syscall table.
- `nfs_uninit()` stops the timer, restores syscall table entries, destroys node hash, and destroys the server request cache.
- `nfs_curusec()` returns monotonic-ish microseconds for write-gather scheduling.

Protocol maps:
- `nfsv3_procid[]` maps old NFSv2 procedure numbers to generic procedure numbers.
- `nfsv2_procid[]` maps generic procedure numbers back to NFSv2.
- `nfsrv_v2errmap[]` maps errno values to NFSv2 errors.
- NFSv3 per-procedure error lists constrain server-returned errors.
- `nfsrv_errmap()` applies v2/v3 error mapping and filtering.

Attribute cache:
- `nfs_loadattrcache()` decodes NFSv2/v3 file attributes from mbufs into `nfsnode` cached attributes, sets vnode type/ops, tracks remote modification via mtime and size changes, and optionally returns a `vattr`.
- `nfs_getattrcache()` validates cached attributes using dynamic age-based timeouts from mount options, accounts for local modifications, updates VM size metadata when needed, and returns cached `vattr` data.

Server helper paths:
- `nfs_namei()` copies a name from RPC mbufs, rejects unsafe names, supports WebNFS public-handle escape decoding, obtains the starting directory from a file handle, sets lookup flags, performs `nlookup()`, and optionally returns parent/target vnodes.
- `nfsrv_fhtovp()` maps an NFS file handle to a vnode, validates export permissions with `VFS_CHECKEXP()`, handles public file handles, applies Kerberos/export-anon/root credential rules, reports read-only exports, and optionally unlocks the vnode.
- `nfs_ispublicfh()` checks for the all-zero public file handle.

Client/cache helpers:
- `netaddr_match()` compares supported network host addresses, currently with special handling for IPv4.
- `nfs_getcookie()` manages per-directory logical-offset to NFS cookie mappings.
- `nfs_invaldir()` invalidates directory cookie/cache metadata.
- `nfs_setvtype()` sets vnode type and initializes VMIO for regular files, directories, and symlinks.
- `nfs_clearcommit()` scans dirty buffers on a mount and clears `B_NEEDCOMMIT`/`B_CLUSTEROK` after a write verifier change.

Credential helpers:
- `nfsrvw_sort()` sorts group lists for comparable server credentials.
- `nfsrv_setcred()` copies and normalizes credentials for server auth.
- `nfs_crhold()` holds or duplicates credentials while discarding jail/prison retention when needed.
- `nfs_crsame()` compares credentials in the subset of fields relevant to NFS.

Important interactions:
- Used by `nfs_serv.c` for server name lookup, file-handle conversion, and error mapping.
- Used by client vnode code for attributes, directory cookies, and vnode typing.
- Coordinates with `nfs_node.c` for `nfsnode` state and with `nfs_socket.c` for initialization/timer globals.

Caveats:
- `nfs_init()` modifies the syscall table directly and preserves the prior `nfssvc` entry for restoration.
- Attribute cache coherency is intentionally heuristic and includes comments noting stale/local-modification edge cases.
- WebNFS/public file-handle handling can cross mount points only in the public lookup path, with callers responsible for final containment checks.
