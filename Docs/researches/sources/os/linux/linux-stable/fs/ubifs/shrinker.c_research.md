# File Research: sources/os/linux/linux-stable/fs/ubifs/shrinker.c

## Purpose
Implements the global Linux VM shrinker for UBIFS TNC znodes, freeing clean cached index subtrees under memory pressure.

## Key Behavior
- Maintains global `ubifs_infos` list and global clean znode counter `ubifs_clean_zn_cnt`.
- `shrink_tnc()` walks a filesystem’s TNC level-order and frees clean znodes old enough for the requested age threshold.
- Whole clean subtrees can be dropped because children of an old clean root are also old enough.
- Znodes on `c->cnext` during commit are skipped because commit state is intentionally not protected by the same mutation path.
- `shrink_tnc_trees()` iterates mounted UBIFS instances fairly, using `umount_mutex` and `tnc_mutex` trylocks to avoid racing unmount and active TNC work.
- `kick_a_thread()` asks a mounted filesystem to start background commit when no clean znodes are currently reclaimable but dirty znodes may become clean.
- `ubifs_shrink_count()` and `ubifs_shrink_scan()` are the shrinker callbacks registered from `super.c`.

## Important Dependencies
- Uses traversal/destruction helpers from `tnc_misc.c`: `ubifs_tnc_levelorder_next()` and `ubifs_destroy_tnc_subtree()`.
- Coordinates with commit state from TNC and journal code through `c->cnext`, `c->cmt_state`, and dirty/clean znode counters.
- Protected by `ubifs_infos_lock`, `c->umount_mutex`, and `c->tnc_mutex`.

## Invariants and Risks
- Clean znode counters may be temporarily negative during commit accounting; count callback clamps this behavior.
- Shrinker must not block heavily or race unmount, so it uses trylocks and reports contention.
- No LRU is maintained by design, avoiding fast-path overhead at the cost of approximate reclaim ordering.
