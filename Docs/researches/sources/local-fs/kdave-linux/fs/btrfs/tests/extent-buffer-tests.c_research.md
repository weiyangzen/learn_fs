# File Research: sources/local-fs/kdave-linux/fs/btrfs/tests/extent-buffer-tests.c

This file tests extent-buffer item splitting, specifically `btrfs_split_item()`.

`test_btrfs_split_item()` creates dummy fs/root/path state and a dummy leaf extent buffer, inserts one checksum item containing `"mary had a little lamb"`, and then splits it twice.

The first split creates two items: the original key at offset 0 with `"mary had a little"` and a new key at offset 3 with `" lamb"`.

The second split splits the first item again, validating memmove behavior in a leaf with existing following items. Expected final chunks are `"mary"`, `" had a little"`, and `" lamb"` with correct keys, sizes, and stored data.

The test intentionally passes NULL transaction handles because it uses a dummy single-level leaf and has enough space to avoid leaf splitting.

`btrfs_test_extent_buffer_operations()` is the file’s public entry point and delegates to `test_btrfs_split_item()`.
