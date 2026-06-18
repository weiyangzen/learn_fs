# File Research: sources/local-fs/btrfs-linux/fs/btrfs/misc.h

## Purpose

Collects small generic helpers used across Btrfs.

## Main Contents

- Cleanup-attribute pointer macros: `AUTO_KFREE` and `AUTO_KVFREE`.
- `ENUM_BIT()` helper for enum-backed bit definitions.
- Bio physical address and block-iteration helpers that support large folios/highmem.
- Bio total-size and full-bio iterator initialization helpers.
- Conditional waitqueue wakeups with and without implied memory barriers.
- Numeric helpers: percentage multiplication and 64-bit power-of-two test.
- Simple bytenr-indexed rb-tree node/search/insert helpers.
- Bitmap range-all-set and range-all-zero tests.

## Key Behaviors

- `cond_wake_up()` relies on `wq_has_sleeper()` barrier semantics.
- `cond_wake_up_nomb()` is only for callers whose preceding operations already imply the necessary barrier.
- `rb_simple_node` must be the prefix of any structure using the simple rb-tree helpers.
