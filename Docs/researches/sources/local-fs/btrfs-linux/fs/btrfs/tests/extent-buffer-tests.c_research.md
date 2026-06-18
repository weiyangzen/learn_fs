# File Research: sources/local-fs/btrfs-linux/fs/btrfs/tests/extent-buffer-tests.c

This file currently tests extent-buffer item splitting through `btrfs_split_item()`. It constructs a dummy fs_info, dummy root, path, and dummy leaf extent buffer, inserts one checksum item containing `"mary had a little lamb"`, then splits it twice.

The first split uses key offset `3` and split length `17`, expecting slot 0 to keep the original key and contain `"mary had a little"`, while slot 1 receives key offset `3` and contains `" lamb"`.

The second split uses key offset `1` and split length `4`, testing memmove of existing items inside the same leaf. It expects three slots: `"mary"` at key offset 0, `" had a little"` at key offset 1, and `" lamb"` at key offset 3.

The test validates item keys, item sizes, and bytes read back from the extent buffer. It deliberately passes a `NULL` transaction handle because the test uses a single dummy leaf with enough room and does not need real tree updates.

`btrfs_test_extent_buffer_operations()` is the public entry point and currently delegates entirely to `test_btrfs_split_item()`.
