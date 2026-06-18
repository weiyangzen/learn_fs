# File Research: sources/os/linux/linux-stable/fs/befs/btree.c

This file implements BeFS B+tree lookup and sequential directory enumeration. The implementation is built on `datastream.c`, so B+tree nodes are read by byte offset from a BeFS datastream rather than directly from raw blocks.

Main exported functions:
- `befs_btree_find()` looks up a string key and returns its stored value, normally an inode block number.
- `befs_btree_read()` returns the Nth key/value pair in sorted order for directory iteration.

Internal flow:
- `befs_bt_read_super()` reads the B+tree superblock from datastream offset 0, converts fields to host byte order, dumps debug info, and validates `BEFS_BTREE_MAGIC`.
- `befs_bt_read_node()` reads a node at a datastream byte offset, keeps the backing `buffer_head`, and converts the node header into `befs_host_btree_nodehead`.
- `befs_btree_find()` loads the tree superblock, reads the root, descends internal nodes through `befs_find_key()`, follows overflow when needed, then searches the final leaf.
- `befs_find_key()` performs binary search inside one node using packed key data, key length index, and value array.
- `befs_btree_read()` seeks to the first leaf with `befs_btree_seekleaf()`, follows right sibling links, and extracts the requested ordinal key.
- `befs_leafnode()` treats nodes with invalid overflow pointer as leaves.
- `befs_bt_keylen_index()`, `befs_bt_valarray()`, and `befs_bt_keydata()` compute packed node subarray locations.
- `befs_bt_get_key()` returns an indexed key pointer and length.
- `befs_compare_strings()` compares B+tree string keys.

Integration:
- Directory lookup in `linuxvfs.c` uses `befs_btree_find()`.
- Directory iteration in `linuxvfs.c` uses `befs_btree_read()`.
- Node reads depend on `befs_read_datastream()` and endian helpers.

Limitations:
- The implementation says it is currently only suitable for directory B+trees.
- Non-string and duplicate-key index support is not implemented; comparison functions for numeric/float key types are disabled under `#if 0`.

Risk notes:
- `befs_bt_get_key()` checks `index > all_key_count`; valid indexes should be `< all_key_count`, so index equal to count is not rejected before indexing the key length array.
- `befs_find_key()` assumes a node has at least one key before it asks for the last key; empty interior cases are mostly handled by seek logic, but malformed nodes may still stress this path.
- `befs_btree_read()` copies keys with `strscpy(keybuf, keystart, keylen + 1)` even though keys are length-delimited packed data; correctness depends on the on-disk key data being NUL-compatible for directory names.
