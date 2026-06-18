# File Research: sources/os/linux/linux-stable/fs/ubifs/budget.c

Purpose: Implements UBIFS space budgeting and free-space reporting.

Key responsibilities:
- Tracks and reserves estimated index growth, new data growth, and dirty-data growth.
- Shrinks liability by writing back dirty inodes/pages.
- Runs garbage collection and commits to recover space when pessimistic budgeting fails.
- Calculates minimum index LEB reservations for the in-the-gaps commit method.
- Calculates available flash space after reserving index, GC, journal heads, deletion, dead space, and dark space.
- Enforces reserved pool rules for root, configured UID/GID, and `CAP_SYS_RESOURCE`.
- Implements `ubifs_budget_space()` and `ubifs_release_budget()`.
- Converts new-page budget into dirty-page budget when a page becomes an update instead of new data.
- Releases dirty inode budget after writeback.
- Reports user-visible free space with UBIFS node and index overhead accounted for.

Important interactions:
- Coordinates with writeback, GC, commit, LEB properties, journal head counts, and UBIFS budget accounting under `space_lock`.
- Uses `commit_sem` around GC and `s_umount` around writeback.

Notable invariants and risks:
- Budgeting is deliberately pessimistic so UBIFS can always flush dirty pages, inodes, and znodes.
- Index space is reserved at roughly three times consolidated index size to preserve commit safety.
- `nospace` and `nospace_rp` are cached flags and require memory barriers when changed.
