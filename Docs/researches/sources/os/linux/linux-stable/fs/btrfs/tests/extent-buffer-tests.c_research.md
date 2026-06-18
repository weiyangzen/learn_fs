# File Research: sources/os/linux/linux-stable/fs/btrfs/tests/extent-buffer-tests.c

## Role
Tests extent-buffer item splitting in a synthetic single-leaf Btrfs tree.

## Main Test
- `test_btrfs_split_item` creates dummy fs_info/root/path state, allocates a dummy extent buffer as a leaf, inserts one checksum item containing `mary had a little lamb`, and then splits it twice with `btrfs_split_item`.
- The first split verifies that slot 0 keeps the original key and contains `mary had a little`, while slot 1 gets the new key offset and contains ` lamb`.
- The second split verifies memmove behavior when splitting an item before an existing item: the leaf ends with three correctly keyed and sized items containing `mary`, ` had a little`, and ` lamb`.
- `btrfs_test_extent_buffer_operations` is the public entry point and delegates to the split-item test.

## Dependencies
Uses dummy fs_info/root helpers, Btrfs path allocation, dummy extent buffers, item insertion, key accessors, and extent-buffer read/write helpers.
