# File Research: sources/os/linux/linux/fs/smb/client/dfs.c

## Purpose
Implements DFS-aware mount traversal and DFS-aware tree reconnect logic for the CIFS/SMB client. It follows DFS referrals, connects to target shares, records origin paths for failover, and reconnects tcons to suitable DFS targets.

## Main Interfaces
- `dfs_parse_target_referral()` converts a DFS referral target into an SMB mount context.
- `dfs_mount_share()` performs DFS-aware mount setup.
- `cifs_tree_connect()` provides the DFS-enabled tree-connect implementation.

## Control Flow
`dfs_mount_share()` starts by optionally resolving the DFS root address for automounts, obtains an initial session, probes for a DFS referral unless `nodfs` is set, and either falls back to ordinary tcon setup or switches into DFS connection mode. DFS traversal uses `dfs_ref_walk` to walk nested referrals up to `MAX_NESTED_LINKS`, trying each target from the DFS cache until a session, tcon, and non-remote path check succeed.

`__dfs_mount_share()` stores the original DFS full path in `tcon->origin_fullpath`, attaches DFS root sessions to the tcon, and schedules the DFS cache refresh worker.

The DFS version of `cifs_tree_connect()` handles IPC normally, then checks whether the TCP server has a `leaf_fullpath` with a cached DFS referral. If so, it parses target shares, filters targets to those matching the current server hostname/IP, updates the DFS target hint, tree-connects to the selected share, and updates the superblock prepath for DFS links.

## State And Synchronization
- Temporarily mutates `ctx->leaf_fullpath`, `ctx->dns_dom`, and `ctx->dfs_root_ses` while obtaining sessions.
- Keeps extra references to DFS root sessions so future referrals can use IPC tcons safely.
- Stores DFS origin path under `tcon->tc_lock`.
- Uses DFS cache target hints to bias future reconnects toward recently successful targets.

## Integration Points
- Calls `dfs_cache_find()`, `dfs_cache_get_tgt_referral()`, `dfs_cache_get_tgt_share()`, and `dfs_cache_noreq_update_tgthint()`.
- Calls `dns_resolve_unc()` and `match_target_ip()` to resolve referral hostnames.
- Calls generic mount helpers from `connect.c`: `cifs_mount_get_session()`, `cifs_mount_get_tcon()`, `cifs_mount_put_conns()`, and `cifs_is_path_remote()`.
- Uses `smb3_parse_devname()` and `smb3_fs_context_fullpath()` to translate referral targets into normal mount context fields.

## Notable Behaviors
- DFS automounts resolve the root UNC before the first session setup, then clear `dfs_automount`.
- Interlink referrals can trigger descent into a nested referral path.
- DFS mounts force later reconnect behavior by setting `ctx->dfs_conn` and re-establishing the session.
- Tree reconnect prefers cached referrals but falls back to the last `tcon->tree_name` when no referral is cached.
- If DFS target prefix paths differ, `cifs_update_super_prepath()` updates the mounted prefix for link targets.

## Risks And Review Focus
- `dfs_ref_walk` cleanup and session reference ownership are critical; missed puts would leak root sessions.
- Context fields are temporarily borrowed and restored, so future changes to `smb3_fs_context` need care.
- Target matching must avoid connecting a tcon to a referral target that does not correspond to the active TCP server.
- Nested DFS traversal must preserve `-ELOOP` behavior and avoid infinite interlink loops.
