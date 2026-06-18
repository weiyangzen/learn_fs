# File Research: sources/os/linux/linux-stable/fs/smb/client/dfs.c

This file implements DFS-aware mount and tree-connect logic for the CIFS/SMB client when `CONFIG_CIFS_DFS_UPCALL` is enabled. It parses DFS referrals, walks nested DFS links, selects targets, updates mount context addressing, and performs DFS target tree connects.

Main responsibilities:
- Converts DFS referral targets into mount context data via `dfs_parse_target_referral()`.
- Resolves target hostnames with `dns_resolve_unc()`.
- Tracks a DFS root SMB session so later referrals can be requested through a valid IPC tcon.
- Walks referral chains with `dfs_ref_walk`, including nested interlinks up to `MAX_NESTED_LINKS`.
- Distinguishes non-DFS mounts from DFS mounts by probing referrals unless `nodfs` is set.
- Rebuilds session/tcon state when a DFS referral target changes the effective server/share.
- Stores `origin_fullpath` on DFS tcons and schedules periodic DFS cache refresh work.
- Implements DFS-aware `cifs_tree_connect()` that can tree-connect to a cached DFS target matching the current TCP session.

Important flows:
- `dfs_mount_share()` first resolves automount root destination when needed, obtains an initial session, probes for referral, and either falls back to ordinary tcon setup or switches into DFS connection mode.
- `__dfs_mount_share()` obtains a canonical origin path, walks referrals, verifies required server/session/tcon pointers, stores DFS origin metadata, and schedules `dfs_cache_work`.
- `__dfs_referral_walk()` iterates targets, parses each target into `ctx`, reconnects session/tcon, checks whether the resulting path is remote, and descends into interlinks when needed.
- DFS tree reconnect uses `tree_connect_dfs_target()` to parse target share/prefix, check whether target host matches the current server, update target hints, and issue the dialect `tree_connect`.

Concurrency and lifetime:
- DFS root session references are explicitly incremented during mount and transferred to `tcon->dfs_ses_list` once the final tcon is known.
- Connection references are released between target attempts with `cifs_mount_put_conns()`.
- `tcon->tc_lock` protects `origin_fullpath` updates.

External dependencies:
- Uses `dfs_cache_find()`, `dfs_cache_noreq_find()`, target iterators, and target hint updates from `dfs_cache.c`.
- Uses core mount helpers from `connect.c`.
- Uses DNS resolution from `dns_resolve.c`.

Research notes:
- The file is the bridge between logical DFS namespace traversal and normal CIFS mount/session/tcon construction.
- DFS interlinks are handled by descending the referral walk stack and restarting target iteration with a new referral path.
- DFS mounts force prefix-path handling and serverino auto-disable in `connect.c` after successful DFS connection.
