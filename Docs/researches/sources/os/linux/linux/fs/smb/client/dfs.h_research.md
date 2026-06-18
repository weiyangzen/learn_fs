# File Research: sources/os/linux/linux/fs/smb/client/dfs.h

## Purpose
Declares DFS traversal structures, helpers, and public DFS mount interfaces used by the CIFS client when DFS upcalls are enabled.

## Main Contents
- Defines `DFS_INTERLINK(v)` to identify referrals that are referral servers but not storage servers.
- Defines `struct dfs_ref`, holding one referral path, full path, root session, target list, and current target iterator.
- Defines `struct dfs_ref_walk`, a bounded stack of referral levels for nested DFS traversal.
- Provides inline traversal helpers for allocation, initialization, cleanup, target iteration, descending/advancing, target hint updates, and tcon session-list transfer.
- Declares `dfs_parse_target_referral()` and `dfs_mount_share()`.
- Provides `dfs_get_path()` and `dfs_get_referral()` wrappers around DFS cache canonicalization and lookup.
- Provides `dfs_put_root_smb_sessions()` and `dfs_ses_refpath()`.

## Control Flow
The header models DFS walking as a small stack. Each level owns its canonical DFS path, user-visible full path, root session reference, and copied target list. `ref_walk_next_tgt()` iterates targets at the current level; `ref_walk_advance()` descends to a deeper level for interlinks; `ref_walk_descend()` backs up when a branch fails.

## State And Ownership
`__ref_walk_free()` releases owned strings, target lists, and session references. `ref_walk_set_tcon()` transfers session references from the walk into `tcon->dfs_ses_list` by linking sessions to the tcon and nulling the walk’s session pointers so cleanup will not put them.

## Integration Points
Included by `dfs.c`, `connect.c`, and DFS cache users. It depends on `dfs_cache.h`, CIFS session/tcon definitions, mount context data, and CIFS Unicode remapping helpers.

## Risks And Review Focus
- The traversal stack is bounded by `MAX_NESTED_LINKS`; changes must preserve loop protection.
- Ownership transfer in `ref_walk_set_tcon()` is easy to break because it intentionally prevents `ref_walk_free()` from putting transferred sessions.
- `dfs_get_referral()` chooses `ctx->dfs_root_ses` when available, otherwise the current mount session; this selection matters for referral IPC routing.
