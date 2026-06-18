# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clport.c

This file is the NetBSD/FreeBSD porting and integration layer for the new NFS client. It provides vnode lookup variants, attribute-cache loading, NFSv4 client identity helpers, weak-cache-consistency parsing, setattr encoding, request dispatch, statfs/fsinfo loading, source-address selection, nfssvc client operations, and module initialization.

Key entry points:
- `newnfs_vncmpf()` compares vnodes against file handles for `vfs_hash`.
- `nfscl_nget()` looks up or creates normal NFS client vnodes/nfsnodes from a consumed `struct nfsfh *`.
- `nfscl_ngetreopen()` finds an existing vnode during NFSv4 reopen recovery without requiring normal blocking vnode locking.
- `nfscl_loadattrcache()` loads `struct nfsvattr` into an nfsnode and optional `struct vattr`.
- `nfscl_fillclid()` constructs an NFSv4 client ID from mount ID, UUID, and random bytes.
- `nfscl_filllockowner()` encodes POSIX/flock lock-owner names.
- `nfscl_getparent()` returns a parent process thread for client recovery logic.
- `nfscl_start_renewthread()` starts the NFSv4 lease-renew kernel thread.
- `nfscl_wcc_data()` parses weak-cache-consistency data.
- `nfscl_postop_attr()` parses post-operation attributes.
- `nfscl_fillsattr()` serializes settable attributes for NFSv2, NFSv3, or NFSv4.
- `nfscl_request()` wraps `newnfs_request()` for client RPC dispatch.
- `nfscl_loadsbinfo()` maps NFS statfs data into `struct statfs`.
- `nfscl_loadfsinfo()` updates mount read/write/readdir sizes and max file size from FSINFO.
- `nfscl_getmyip()` selects the local source address used to reach the server.
- `newnfs_copyincred()` copies kernel credentials into NFS credential form.
- `nfscl_init()` performs one-time client initialization.
- `nfscl_checksattr()` removes no-op setattr fields and ensures time fields for verifier-related SETATTR behavior.
- `nfscl_maperr()` maps NFSv4 protocol errors to local errno values.
- `nfscl_procdoesntexist()` validates an encoded POSIX lock owner against the process table.
- `nfssvc_nfscl()` handles client-facing `nfssvc()` operations for callback sockets, callback daemons, and mount-option dumping.
- `nfscl_modevent()` initializes the full client module.

Important behavior:
- `nfscl_nget()` attaches NFSv4 directory file handle and component name state to regular files so later `OPEN` operations can be issued.
- Existing NFSv4 regular-file nodes may have their saved parent/name tuple replaced if the same file handle is found through a different lookup name.
- `nfscl_loadattrcache()` rejects changed file IDs with `EIDRM` and rate-limited warnings, protecting against broken servers or middleware returning attributes for the wrong object.
- Attribute-cache size updates are careful around locally modified files: local size can win over smaller server size, larger server size can set `NSIZECHANGED`, and VM pager size changes may be deferred until after unlocking.
- NFSv4 fsid handling may synthesize `va_fsid` from per-node fsids so `getcwd(3)` works across server-side mounted subtrees.
- `nfscl_fillsattr()` emits version-specific setattr encodings, including NFSv3 guarded boolean fields and NFSv4 attribute bitmaps.
- `nfssvc_nfscl()` supports `NFSSVC_CBADDSOCK`, `NFSSVC_NFSCBD`, and `NFSSVC_DUMPMNTOPTS`.

Module integration:
- Defines global mutexes `nfs_clstate_mutex` and `ncl_iod_mutex`.
- On `MOD_LOAD`, calls `newnfs_portinit()`, initializes mutexes, initializes NFS client state, initializes callback RPC state, installs `ncl_call_invalcaches`, and installs `nfsd_call_nfscl`.
- Module unload is effectively unsupported; it returns busy if callback daemons exist and otherwise falls through to `EOPNOTSUPP`.
- Declares dependencies on `nfscommon`, `krpc`, `nfssvc`, and `nfslock`.

Research notes:
- This file is the highest-level integration surface in the group.
- The most security/data-integrity-relevant logic is file-handle identity handling, fileid-change detection, attribute-cache size reconciliation, callback `nfssvc()` socket intake, and NFSv4 error mapping.
