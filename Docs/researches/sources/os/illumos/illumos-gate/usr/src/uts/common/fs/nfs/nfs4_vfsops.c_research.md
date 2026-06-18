# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_vfsops.c

NFSv4 VFS implementation for illumos: module/VFS registration, mount argument ingestion, root vnode creation, mount-root support, unmount/freevfs handling, server/clientid lifecycle, referrals, symlink resolution during mount, replica/failover server lists, and SETCLIENTID lease setup.

Key responsibilities:
- Registers NFSv4 VFS and vnode operation tables in `nfs4init()` and releases module-level VFS state in `nfs4fini()`.
- Copies and validates user mount arguments in `nfs4_copyin()`, including transport config, server address, server path, hostname, secure mount data, AUTH_DH/RPCSEC_GSS security data, and failover-linked argument chains.
- Frees copied mount arguments with `nfs4_free_args()` and deep-copies security data with `copy_sec_data()` / `copy_sec_data_gss()`.
- Implements `nfs4_mount()`: permission checks, remount restrictions, trigger-stub handling for ephemeral mounts, transport validation, servinfo chain construction, RDMA substitution, security flavor setup, failover-list validation, zone/labeled-system policy checks, root vnode acquisition, SETCLIENTID setup, mount option application, and ephemeral mount recording.
- Resolves mount-time symlinks and referrals through `getlinktext_otw()`, `resolve_sympath()`, `resolve_referral()`, `update_servinfo4()`, `extract_referral_point()`, and `setup_newsvpath()`.
- Gets root filehandles and filesystem capabilities in `nfs4getfh_otw()`, building `PUTROOTFH`/`PUTPUBFH`, `GETFH`, `LOOKUP`, and `GETATTR` compounds, handling `NFS4ERR_SYMLINK`, `NFS4ERR_MOVED`, recovery-worthy errors, stale mount retries, and server fsinfo limits.
- Creates the mount state in `nfs4rootvp()`: initializes `mntinfo4_t`, VFS device/fsid fields, async queues/threads, per-mount locks/lists/kstats, shared filehandle table, open-owner state, root vnode, root/parent filehandles, zone references, and replica filtering.
- Implements VFS operations: `nfs4_unmount()`, `nfs4_root()`, `nfs4_statvfs()`, `nfs4_sync()`, `nfs4_vget()` returning `EREMOTE`, `nfs4_mountroot()` for diskless root, and `nfs4_freevfs()`.
- Manages client identity and lease state with global `nfs4_server_lst`, `nfs4setclientid()`, `nfs4setclientid_otw()`, server creation, mount-to-server list insertion/removal, lease-thread start/termination, and server refcount teardown.
- Supports failover server movement via `nfs4_move_mi()`, moving an `mntinfo4_t` from one `nfs4_server_t` to another and preserving open-file state counts.
- Handles forced unmount cleanup through `async_free_mount()`, `nfs4_free_mount_thread()`, and `nfs4_free_mount()`, waiting for outstanding over-the-wire calls and recovery before removing server linkage and destroying rnodes.

Major dependencies:
- Kernel VFS/vnode interfaces, mount argument ABI, zones, credentials, labeled security policy, kstats, kmem, CPR callbacks, async thread creation, DNLC, and root boot helpers.
- RPCSEC/AUTH_DH/RPCSEC_GSS security modules.
- NFSv4 client internals: compound calls, recovery framework, rnode table, shared filehandle table, async manager, inactive thread, ephemeral/mirror mount support, callbacks, lease renewal, open-owner tracking, referrals, and mount option parsing.

Important control flow:
- Regular mount path: `nfs4_mount()` copies args, builds `servinfo4_t` list, calls `nfs4rootvp()`, calls `nfs4setclientid()`, applies options, and records ephemeral mount metadata if needed.
- Root filehandle path: `nfs4rootvp()` initializes mount state first, then each replica is probed by `nfs4getfh_otw()`; duplicate or failing replicas are marked `SV4_NOTINUSE`, and the first usable server becomes `mi_curr_serv`.
- Mount-time path traversal retries failed stale/symlink/referral cases by restoring a saved `servinfo4_t` snapshot and redriving the lookup compound up to `nfs4_max_mount_retry`.
- SETCLIENTID path: find or create a shared `nfs4_server_t`, serialize pending clientid setup with `N4S_CLIENTID_PEND`, issue `SETCLIENTID` plus `SETCLIENTID_CONFIRM`, cache lease time and propagation delay, attach the mount to the server, and start lease renewal if needed.
- Normal unmount stops async work, flushes rnodes, handles ephemeral tree activation, removes the mount from server and zone lists, and relies on freevfs to drop the initial `mntinfo4_t` hold.
- Forced unmount marks the VFS unmounted and frees mount state asynchronously when possible.

Concurrency and locking:
- `nfs4_server_lst_lock` protects the global server list; each `nfs4_server_t` has `s_lock`.
- `mi_recovlock` controls mount/server linkage relative to recovery and over-the-wire operations.
- Mount/unmount state uses `mi_lock`, async locks/CVs, rnode-list locks, and server pending/clientid CVs.
- Forced unmount cleanup waits for `s_otw_call_count` and `mi_in_recovery` to drain before breaking server links.
- Zone references and VFS references are deliberately held while mount records are visible through server lists or worker threads.

Notable risks:
- Mount setup is partially initialized before the first root lookup succeeds; every error path must release zone refs, async threads, rnodes, servinfo chains, kstats, and `mntinfo4_t` holds consistently.
- `copy_svp()` appears to copy `svp->sv_dhsec` from the newly allocated target rather than the source, so AUTH_DH saved-state behavior should be reviewed if this path is active.
- Referral and symlink path rewriting uses fixed `MAXPATHLEN` buffers and slash-counting logic; malformed or edge-case paths can stress truncation/error handling.
- `nfs4getfh_otw()` encodes detailed assumptions about compound result positions; any change in lookup compound construction must keep index math synchronized.
- SETCLIENTID retry and `NFS4ERR_CLID_INUSE` handling intentionally has limited robustness, as noted by in-code comments.
- Server refcounts, VFS holds, and mount list links are tightly coupled; incorrect removal while open files remain can break lease renewal or recovery lookup paths.
