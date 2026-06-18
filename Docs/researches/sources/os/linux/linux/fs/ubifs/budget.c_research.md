# File Research: sources/os/linux/linux/fs/ubifs/budget.c

Purpose: UBIFS budgeting and free-space accounting. It pessimistically reserves space for data, dirty data, and index growth so operations can later be committed safely.

Key APIs:
- `ubifs_calc_min_idx_lebs`
- `ubifs_calc_available`
- `ubifs_budget_space`
- `ubifs_release_budget`
- `ubifs_convert_page_budget`
- `ubifs_release_dirty_inode_budget`
- `ubifs_reported_space`
- `ubifs_get_free_space_nolock`
- `ubifs_get_free_space`

Implementation notes:
- `make_free_space()` tries writeback, GC, then commit, retrying up to `MAX_MKSPC_RETRIES`.
- Index budgeting reserves roughly three times consolidated index size to support the in-the-gaps commit method.
- Available space subtracts GC reserve, journal heads, deletion reserve, dead/dark space, and excess index dark space.
- Reserved pool access is allowed for configured UID, `CAP_SYS_RESOURCE`, or configured GID membership.
- Budget requests calculate separate `idx_growth`, `data_growth`, and `dd_growth`.
- Released index growth moves into `uncommitted_idx` until commit clears it.

Concurrency and correctness:
- `space_lock` protects budget info and no-space flags.
- Writeback uses `s_umount` read lock.
- GC runs under `commit_sem` read lock.
- `nospace` and `nospace_rp` flags use memory barriers around updates.
- Assertions enforce bounded request shapes and alignment.
