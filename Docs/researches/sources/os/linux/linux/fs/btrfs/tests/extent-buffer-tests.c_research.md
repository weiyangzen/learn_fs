# File Research: sources/os/linux/linux/fs/btrfs/tests/extent-buffer-tests.c

Read completely: 223 lines.

This file tests `btrfs_split_item()` on a dummy leaf extent buffer.

`test_btrfs_split_item()`:
- Allocates dummy fs_info, root, path, and extent buffer.
- Inserts one item with key `(0, BTRFS_EXTENT_CSUM_KEY, 0)` and payload `"mary had a little lamb"`.
- Splits the item at offset 17 with new key offset 3, expecting:
  - slot 0: original key, payload `"mary had a little"`
  - slot 1: key offset 3, payload `" lamb"`
- Splits the first item again at offset 4 with new key offset 1, expecting:
  - slot 0: `"mary"`
  - slot 1: `" had a little"`
  - slot 2: `" lamb"`

The test verifies keys, item sizes, and copied payload contents after each split.

`btrfs_test_extent_buffer_operations()` is the file entry point and runs the split-item test.

Correctness focus:
- Splitting an item must preserve original key/payload prefixes, create the right new key and suffix, and memmove later items correctly.
- The test intentionally uses a single dummy level-0 leaf and NULL transaction handle because no tree split is needed.
