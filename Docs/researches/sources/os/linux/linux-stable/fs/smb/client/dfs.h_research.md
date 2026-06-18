# File Research: sources/os/linux/linux-stable/fs/smb/client/dfs.h

This header defines DFS referral-walk structures and inline helpers used by `dfs.c` and DFS-enabled connection paths.

Main contents:
- `DFS_INTERLINK(v)` identifies referrals that point to another DFS namespace link rather than a storage server.
- `struct dfs_ref` stores one referral-walk level: canonical path, full path, root session reference, target list, and current target iterator.
- `struct dfs_ref_walk` stores the active mount context and a fixed `MAX_NESTED_LINKS` stack of `dfs_ref` entries.
- Inline accessors and helpers manage referral-walk start/current/end positions, target iteration, target hint updates, descent, cleanup, and tcon session transfer.

Important helpers:
- `ref_walk_alloc()`/`ref_walk_init()` allocate and initialize a walk.
- `ref_walk_free()` frees all paths, target lists, and retained SMB sessions.
- `ref_walk_advance()` moves deeper into nested DFS referrals and returns `-ELOOP` if nesting exceeds the fixed stack.
- `ref_walk_next_tgt()` iterates targets and marks end-of-list with an `ERR_PTR(-ENOENT)` sentinel.
- `ref_walk_get_tgt()` converts the current target iterator into a `dfs_info3_param`.
- `ref_walk_set_tcon()` moves retained DFS root session references onto the final tcon’s `dfs_ses_list`.
- `dfs_get_path()` canonicalizes a path through the DFS cache helper.
- `dfs_get_referral()` fetches or refreshes a referral using the DFS root session when available.
- `dfs_put_root_smb_sessions()` releases root-session references stored on a list.
- `dfs_ses_refpath()` returns the canonical referral path for a DFS session.

Research notes:
- This header encodes DFS mount traversal state as a bounded stack, which is important for loop prevention.
- Cleanup is ownership-aware: once sessions are moved to `tcon->dfs_ses_list`, the walk no longer releases them.
