# sources/user-network-fs/nfs-ganesha/src/support/exports.c

## Purpose
`exports.c` parses, validates, commits, updates, logs, initializes, and releases NFS-Ganesha exports. It owns the export configuration grammar for `EXPORT`, `PSEUDOFS`, `EXPORT_DEFAULTS`, and `Client` blocks; computes effective permissions; connects exports to FSAL/MDCACHE; initializes export root objects; handles reread/update pruning; and checks request access/security against export and client policy.

## Important APIs, Types, And Functions
Global defaults are held in `export_opt` and the staging copy `export_opt_cfg`, protected by `export_opt_lock`. `GLOBAL_EXPORT_PERMS_INITIALIZER` sets built-in defaults such as anonymous ids, attr expiry, root squash, no access, default auth/transport inheritance, and no delegations.

Config and commit helpers:

- `StrExportOptions()`, `LogExportClientListEntry()`, `LogExportClients()`, `log_an_export()`, and `log_all_exports()` format export/client permissions.
- `client_init()`, `pseudofs_client_init()`, `client_commit()`, `export_client_allocator()`, `export_client_filler()`, and `client_adder()` build client lists with per-client permissions and HA proxy protocol matching mode.
- `fsal_cfg_commit()` loads/initializes an FSAL, calls `mdcache_fsal_create_export()`, attaches `export->fsal_export`, and clamps read/write sizes to FSAL maxima.
- `fsal_update_cfg_commit()` updates an existing FSAL export through `mdcache_fsal_update_export()` and handles delegation-option transition hooks for Ceph builds.
- `export_commit_common()` is the main validation and insertion/update routine for initial, add, and update commits.
- `pseudofs_fsal_commit()`, `pseudofs_commit()`, `add_export_commit()`, `update_export_commit()`, and `update_pseudofs_commit()` adapt common commit logic for block type.
- `export_defaults_commit()` atomically swaps parsed defaults into `export_opt`.

Runtime APIs:

- `ReadExports()` reads defaults, optional `PSEUDOFS`, all `EXPORT` blocks, creates a default pseudo-root if needed, and logs exports.
- `reread_exports()` serializes under `EXPORT_ADMIN_LOCK()`, reloads defaults/pseudo/exports using update descriptors, prunes defunct exports, and rebuilds PseudoFS.
- `exports_pkginit()` initializes root objects for all manager-registered exports and reverts failed ones.
- `init_export_root()` resolves the FSAL path, sets dynamic IO sizes, stores the root object, and records export-root state in the object junction.
- `nfs_export_get_root_entry()` returns a referenced root object and validates it is a directory.
- `release_export()` unlinks root state, unmounts PseudoFS when not config-only, marks stale, calls FSAL `prepare_unexport()` and `unexport()`, releases state, and removes the export from the manager.
- `free_export_resources()` releases client lists, FSAL exports/modules, QoS state, strings, refstrings, and temporary op context state.
- `export_check_security()`, `get_anonymous_uid()`, `get_anonymous_gid()`, and `export_check_access()` compute request authorization.

## Control Flow
Initial config load starts in `ReadExports()`. It derives default protocol bits from `NFS_options`, loads `EXPORT_DEFAULTS`, loads `PSEUDOFS`, loads each `EXPORT`, and then calls `build_default_root()` if neither export id 0 nor pseudo `/` exists. Each export block allocates a `gsh_export`, processes scalar parameters, processes `Client` blocks, processes the `FSAL` block last, and reaches `export_commit_common()`.

`export_commit_common()` validates pseudo path syntax, export id 0 rules, NFSv4 pseudo requirements, protocol/transport compatibility with core options, `mount_path_pseudo`, duplicate id/tag/pseudo/path rules, and FSAL availability. For new dynamic exports it initializes the export root and mounts into PseudoFS before manager insertion. For initial exports it inserts first and queues later mounting. For updates it fetches the existing export, rejects immutable tag/path/filesystem-id changes, detects pseudo or NFSv4 mountability changes, sets remount/prune flags, copies mutable fields into the existing export, and disposes of the staging export.

Runtime access checks use `export_check_access()`. It starts from no access, optionally matches a specific client entry from the export list or default client list, overlays export permissions, overlays `EXPORT_DEFAULTS`, and finally overlays built-in defaults. `export_check_security()` then validates RPC auth flavor and RPCSEC_GSS service against `op_ctx->export_perms`.

Reread uses a new parse generation. Updated exports receive the current generation. After parsing, `prune_pseudofs_subtree()`, `prune_defunct_exports()`, and `create_pseudofs()` remove older exports and remount changed/new reachable exports.

## State And Persistence Behavior
The file mutates in-memory export structures created from configuration. No on-disk persistence is written. `export_opt_cfg` is a staging object so default updates can be swapped into `export_opt` under `export_opt_lock`. Export fullpath and pseudopath have both config strings and RCU/refcounted `gsh_refstr` values; `copy_gsh_export()` swaps refstrings with `synchronize_rcu()` before releasing old values.

Per-export mutable options are split between atomic scalar fields (`MaxRead`, `MaxWrite`, preferred sizes, offsets, options) and fields protected by `exp_lock` (permissions, client lists, path refstrings, root/junction pointers). FSAL export lifetime is reference-balanced with `fsal_put()` and the FSAL export `release()` op. Root object lifetime is managed through object references, junction locks, `export_root_object_get/put()`, and `exp_root_refcount`.

## Dependencies And Integration Points
Major dependencies include `config_parsing`, `client_mgr` style client matching through `add_client()` and `client_match()`, `ip_utils` for address display and matching support, FSAL module lookup/load/update, MDCACHE FSAL stacking, PseudoFS mount/prune/create functions, pNFS utilities, NFS state cleanup, QoS optional code, HA proxy transport metadata, and global `op_ctx`.

The config descriptors exported from this file are used by DBus dynamic add/update paths in `export_mgr.c`. `ReadExports()` and `reread_exports()` are higher-level startup/reload entry points used by server initialization and SIGHUP/admin reload flows.

## Risks And Edge Cases
`valid_pseudopath()` returns false for `NULL`, and `export_commit_common()` calls it unconditionally before later logic that discusses exports without a pseudo path. If non-NFSv4 exports are still expected to support no `Pseudo`, this ordering makes pseudo path effectively mandatory and should be confirmed against intended behavior.

`export_check_client_options()` walks `exp->clients` without taking `exp->exp_lock` in the visible function. If callers do not already serialize, concurrent export update can race with client-list swapping.

`copy_gsh_export()` deliberately swaps client lists between the live export and staging export so later disposal frees old clients. This is subtle and tests should verify no double-free or stale pointer remains after update failures and successes.

The root object reference choreography in `init_export_root()` and `release_export()` is delicate: lookup references, extra root references, junction list membership, and two `put_ref()` calls must stay balanced across error and config-only cleanup paths.

HA proxy matching relies on `op_ctx->nfs_reqdata->svc.rq_xprt`. Callers invoking `export_check_access()` outside a normal request path must ensure `nfs_reqdata` is valid or that the client matching callback cannot dereference a null request.

## Test Signals
Strong signals include config tests for `EXPORT_DEFAULTS` overlay order, client block parsing, duplicate id/tag/pseudo/path handling, export id 0 constraints, no-pseudo non-v4 exports if supported, dynamic add/update/remount flows, reread generation pruning, FSAL create/update failure cleanup, root object reference cleanup under sanitizer, HA proxy client matching, auth flavor rejection, anonymous uid/gid fallback, and read access check policy formatting.
