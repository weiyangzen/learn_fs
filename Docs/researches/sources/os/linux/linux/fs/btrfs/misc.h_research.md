# File Research: sources/os/linux/linux/fs/btrfs/misc.h

This header contains small generic Btrfs utility macros and inline helpers.

Utilities:
- `AUTO_KFREE()` and `AUTO_KVFREE()` define cleanup-attribute pointers initialized to NULL.
- `ENUM_BIT()` defines enum values that represent bit masks.
- `bio_iter_phys()` returns the physical address for a bio iterator’s current bvec.
- `btrfs_bio_for_each_block()` and `btrfs_bio_for_each_block_all()` iterate bios in filesystem block-sized chunks.
- `bio_get_size()` sums all bvec lengths in a non-cloned bio.
- `init_bvec_iter_for_bio()` creates a full-size iterator for a bio.

Wait and math helpers:
- `cond_wake_up()` wakes a waitqueue only if sleepers exist and relies on the full barrier implied by `wq_has_sleeper()`.
- `cond_wake_up_nomb()` is a no-extra-barrier variant for paths where previous code already supplies ordering.
- `mult_perc()` computes a percentage of a 64-bit value.
- `is_power_of_two_u64()` and `has_single_bit_set()` provide 64-bit-safe single-bit checks.

Simple rbtree helpers:
- `struct rb_simple_node` is a bytenr-keyed node prefix.
- `rb_simple_search()` finds an exact bytenr.
- `rb_simple_search_first()` finds the first node at or after a bytenr.
- `rb_simple_insert()` inserts by bytenr with `rb_find_add()`.

Bitmap helpers:
- `bitmap_test_range_all_set()` and `bitmap_test_range_all_zero()` test whether a bitmap range is entirely set or clear.

Design notes:
- This header collects low-level helpers used across unrelated Btrfs subsystems.
- Several helpers assume caller-level constraints, such as non-cloned bios or structures beginning with the expected rbtree prefix.
