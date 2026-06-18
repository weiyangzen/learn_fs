
# sources/user-network-fs/nfs-ganesha/src/SAL/recovery/recovery_fs.c

## Purpose

`recovery_fs.c` implements the legacy filesystem-backed NFSv4 recovery backend for nfs-ganesha. It persists confirmed client IDs, NFSv4 reclaim-complete markers, and revoked delegation file handles in a directory tree under configured recovery root directories so a restarted server can enter grace, rebuild the reclaim allowlist, and reject `DELEG_PREV` reclaims for already revoked delegations.

## Important APIs, types, and functions

- Global storage paths: `v4_recov_dir`, `v4_recov_dir_len`, `v4_old_dir`, and `v4_old_dir_len` are shared with filesystem recovery variants through `recovery_fs.h`.
- `fs_create_recov_dir()` creates the configured recovery root, current directory, old directory, and optional clustered `node%d` subdirectories. It populates the global path buffers and returns negative errno-style failures.
- `fs_add_clid()` creates a persistent directory path for a confirmed client. It calls `fs_create_clid_name()` to build `cid_recov_tag`, then splits long names into `NAME_MAX` path segments.
- `fs_reclaim_complete()` records an OP_RECLAIM_COMPLETE marker by creating a `reclaim_complete` file under the final client directory.
- `fs_rm_clid()` and recursive helper `fs_rm_clid_impl()` remove the client directory hierarchy and embedded files for normal client destruction/expiry.
- `fs_read_recov_clids_takeover()` is the backend read hook. It handles cold restart with no `nfs_grace_start_t`, IP takeover, nodeid takeover, and update-client events.
- `fs_read_recov_clids_impl()` recursively reconstructs split client names, validates their `<IP>-(len:value)` format, calls `add_clid_entry()`, copies revoked file handles, and optionally moves entries into the old directory.
- `fs_clean_old_recov_dir_impl()` recursively deletes old recovery trees after grace.
- `fs_add_revoke_fh()` base64url-encodes an NFS file handle and persists it as a file prefixed by byte `0x01` under the client directory.
- `fs_backend` wires these functions into `struct nfs4_recovery_backend`.

## Control flow

Initialization builds current and old recovery paths from `nfs_param.nfsv4_param.recov_root`, `recov_dir`, and `recov_old_dir`. If `recovery_backend_ipbased` is disabled and clustering is active, it appends `/node%d`; if IP-based recovery is enabled, per-IP directories are formed later with `fs_make_ip_recov_dir_name()`.

When a client becomes persistent, `fs_add_clid()` derives a name from the server/client address and opaque client owner value. Printable opaque values without slashes are copied directly; other values are rendered as opaque bytes. The name is wrapped with an explicit length field and split into nested directories so filesystem `NAME_MAX` is not exceeded.

On restart, `fs_read_recov_clids_recover()` first reads the old directory, then reads current and moves/copies entries into old. The recursive read helper treats a directory leaf whose reconstructed name validates as one client entry. It checks for the reclaim marker, adds the client to the in-memory reclaim list, imports revoke files through `add_rfh_entry()`, and deletes current entries when not in takeover mode. During takeover, it reads the failed peer's path but leaves source records in place.

At end of grace, `fs_clean_old_recov_dir()` removes old entries recursively. Client removal performs a recursive postorder traversal, deletes revoke files and reclaim markers at the leaf, and removes directories up the tree.

## State and persistence behavior

The persistent format is directory-oriented. A client is represented by one path whose segment concatenation is the client recovery tag. Revoked delegation handles are regular files below that path whose names begin with `0x01` followed by base64url file-handle text. OP_RECLAIM_COMPLETE is represented by a regular file named `reclaim_complete`.

The backend uses two directories: current records for active clients and old records for the previous boot/grace epoch. Current records are copied/moved into old during recovery so a restart during grace can still recover clients. IP-based mode adds per-server-address recovery directories, while clustered node mode adds node-specific subdirectories.

## Dependencies and integration points

The file depends on SAL/NFS recovery hooks (`add_clid_entry_hook`, `add_rfh_entry_hook`, `nfs_grace_start_t`), client structures (`nfs_client_id_t`, `nfs_client_record_t`), path configuration in `nfs_param`, global cluster node id `g_nodeid`, display helpers, `bsd-base64`, and FSAL file-handle conversion indirectly through revocation consumers. It integrates with the generic NFSv4 recovery layer through `fs_backend_init()` and with delegation revocation through `nfs4_record_revoke()` callers that invoke `.add_revoke_fh`.

## Risks and edge cases

- Several paths depend on `struct dirent.d_type`; filesystems that return `DT_UNKNOWN` may be skipped or logged as unknown.
- The client recovery tag parser uses `atoi()` and manual substring checks; malformed directory trees are ignored but still can accumulate until cleanup.
- Long path handling is defensive, but recursive allocation and `PATH_MAX` assumptions remain central to correctness.
- IP-based removal has a branch that logs an expired v4.1 client path but does not remove it, which looks intentional or unfinished and should be reviewed with IP takeover semantics.
- `fs_add_revoke_fh()` asserts that `cid_recov_tag` is present and the base64 encode succeeds; unexpected call ordering becomes process-fatal in assert-enabled builds.
- Non-atomic directory moves/cleanup mean crash windows are mitigated by current/old directories but not eliminated.

## Test signals

Useful tests should cover restart with current-only records, restart with old records, crash during grace, long client owner strings split across several `NAME_MAX` components, malformed recovery directories, reclaim-complete marker presence/absence, revoke file import and deletion, IP-based recovery naming, clustered node directories, and end-grace cleanup. Integration tests should verify `add_clid_entry()` receives the expected `reclaim_complete` boolean and revoked handle strings.
