# File Research: sources/os/linux/linux/fs/ubifs/shrinker.c

Read completely: 319 lines.

This file implements the global UBIFS VM shrinker for reclaiming clean TNC znodes across all mounted UBIFS instances.

Main entry points: `ubifs_shrink_count` and `ubifs_shrink_scan`. Global state includes `ubifs_infos`, `ubifs_infos_lock`, `ubifs_clean_zn_cnt`, and the per-run `shrinker_run_no`.

Key behavior: `shrink_tnc` walks a filesystem's TNC in level-order and frees clean znodes older than the requested age. Because old clean subtree roots imply old clean descendants, entire subtrees can be detached and destroyed through `ubifs_destroy_tnc_subtree`.

Global scan policy: `shrink_tnc_trees` iterates mounted UBIFS instances, protects unmount races with `ubifs_infos_lock` and `c->umount_mutex`, uses `mutex_trylock` for both unmount and TNC locks, moves visited filesystems to the tail for fairness, and stops once enough znodes are reclaimed.

Commit prompting: when no clean znodes are globally available, `kick_a_thread` looks for a mounted writable filesystem with dirty znodes and a resting commit state, then requests background commit so dirty znodes may become clean and reclaimable later.

Age policy: `ubifs_shrink_scan` first tries `OLD_ZNODE_AGE`, then `YOUNG_ZNODE_AGE`, then age zero. If no nodes are freed but lock contention occurred, it returns `SHRINK_STOP`; otherwise it returns the number freed.

Important interactions: `super.c` registers the shrinker at module init and maintains `ubifs_infos` during mount/unmount. `tnc_misc.c` supplies level-order traversal and subtree destruction. `tnc_commit.c` updates clean/dirty znode counters after commit.

Reliability notes: znodes on the commit `cnext` ring are deliberately skipped because that list is not protected by the normal TNC mutex during commit. The clean-znode counters may briefly be negative by design, so `ubifs_shrink_count` clamps negative values to a nonzero retry hint.
