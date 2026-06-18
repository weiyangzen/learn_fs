# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_bulkfree.c

## Purpose
Implements HAMMER2's bulk-free pass: a background/manual recovery-style scanner that reconstructs live allocation state from reachable blockrefs, compares it with the live freemap, and advances two-stage free transitions.

## Key Elements
- `hammer2_bulkfree_scan()` walks topology from a referenced unlocked parent, locks each parent shared with data resolution, uses `hammer2_chain_scan()` to iterate blockrefs, counts inode/dirent/chain/byte statistics, skips unsafe recursion on CRC-check errors, and bounds recursion by saving chains in a TAILQ when depth or saved-chain limits are exceeded.
- `hammer2_bulkfree_pass()` clears the live dedup cache, allocates a swap-backed in-memory freemap window, repeatedly scans the volume over storage ranges sized by the supplied bulkfree buffer, drains deferred chains, and only syncs freemap state if the scan was not aborted.
- `cbinfo_bmap_init()` initializes each 4MB in-memory freemap segment, marking reserved/out-of-media ranges as fully allocated/unavailable and normal usable ranges as fully free before live blockrefs are replayed.
- `h2_bulkfree_callback()` processes each reachable blockref in the current storage window, throttles non-leaf scanning with `hammer2_bulkfree_tps`, updates segment class/avail/linear metadata, and marks corresponding 16KB freemap bitmap cells as allocated (`11`).
- `h2_bulkfree_sync()` iterates live freemap leaves through the device freemap chain, skips unchanged segments when bitmap/linear/bigmask are already acceptable, modifies changed freemap leaves, resets the relaxed allocation heuristic, and calls the adjust routine.
- `h2_bulkfree_sync_adjust()` applies the transition rules: memory `00` versus live `11` becomes live `10`, memory `00` versus live `10` becomes live `00`, memory `11` versus live `10` becomes live `11`, and unexpected live-free-to-allocated repairs are counted and warned.
- `h2_bulkfree_test()` is an 8-way dedup heuristic keyed by `data_off`; it avoids repeatedly descending already-seen physical trees and preserves saved errors for duplicate references.
- `bigmask_get()` and `bigmask_good()` compute/check permissive freemap allocation-size availability masks used for sync shortcuts.

## Dependencies
Uses HAMMER2 chain traversal, freemap allocation metadata, device volume data locking/modification, swap-backed kernel memory, DragonFly sleep/signal/tick primitives, HAMMER2 dedup cache helpers, and global tuning knobs such as `hammer2_limit_saved_depth`, `hammer2_limit_saved_chains`, `hammer2_bulkfree_tps`, `hammer2_debug`, and `hammer2_aux_flags`.

## Behavior/Risks
- Designed to run concurrently with frontend operations by scanning a synchronized volume snapshot and relying on the two-stage freemap transition to avoid freeing newly allocated blocks.
- Aborts on user/kernel signal and avoids synchronizing a partial in-memory freemap after abort.
- Continues through CRC check errors where possible, but refuses to recurse through corrupt block tables because they can loop indefinitely or panic the scanner.
- Correctness depends on complete topology traversal, valid blockref `data_off`/radix boundaries, and no allocation crossing HAMMER2's 1GB L1 or 4MB L0 freemap boundaries; boundary violations are logged and clipped.
- Emergency/recovery value is high, but this file directly mutates freemap state and volume free-space accounting, so bugs can create leaks or false frees.
