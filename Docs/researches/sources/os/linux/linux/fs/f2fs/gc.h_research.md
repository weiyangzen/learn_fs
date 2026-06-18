# File Research: sources/os/linux/linux/fs/f2fs/gc.h

Read completely: 202 lines.

## Summary
Defines F2FS garbage-collection constants, background-GC thread state, temporary GC inode/victim structures, free-space accounting helpers, sleep-time adjustment helpers, and GC boost heuristics.

## Main Contents
- GC thread sleep defaults for regular and zoned devices.
- Age-threshold GC defaults: age threshold, candidate ratio, max candidates, age weight, and accuracy class.
- Invalid/free block percentage thresholds for background GC triggering.
- Zoned-device no-GC and boost-GC thresholds.
- Pinned-file and victim-search defaults.
- `struct f2fs_gc_kthread`.
- `struct gc_inode_list`.
- `struct victim_entry`.
- Inline helpers for free block accounting, sleep adjustments, and GC boost decisions.

## Important Behavior
`free_segs_blk_count_zoned()` sums usable blocks per free segment, accounting for zoned devices whose zone capacity can be smaller than zone size. Non-zoned accounting can use segment counts directly.

`free_user_blocks()` subtracts overprovisioned space from free segment blocks. `has_enough_invalid_blocks()` triggers background GC when invalid blocks are high and free user blocks are low. `need_to_boost_gc()` uses zoned free-block thresholds for zoned devices and invalid-block pressure for non-zoned devices.

Sleep helpers increase, decrease, or reset the GC thread wait interval within configured min/max/no-GC limits.

## Risks
The constants here directly tune GC aggressiveness and latency. Zoned devices depend on usable-block accounting rather than raw segment counts. Changing threshold defaults can alter write amplification, free-space recovery latency, and foreground-GC frequency.
