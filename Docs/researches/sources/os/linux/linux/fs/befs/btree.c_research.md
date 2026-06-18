# File Research: sources/os/linux/linux/fs/befs/btree.c

## Purpose
Implements read-only traversal and lookup for BeFS B+trees, primarily directory indexes. It sits above `datastream.c`, which maps logical tree offsets to disk blocks.

## Main Functions
- `befs_bt_read_super()`: reads the B+tree superblock from datastream offset 0, converts fields to CPU byte order, dumps debug information, and validates `BEFS_BTREE_MAGIC`.
- `befs_bt_read_node()`: reads a B+tree node at a byte offset, handles buffer replacement, converts node header fields, and stores pointers into the buffer.
- `befs_btree_find()`: public exact string-key lookup. It reads the tree superblock, descends internal nodes via `befs_find_key()`, follows overflow links where needed, then searches the leaf and returns the stored value.
- `befs_find_key()`: binary search inside one node. It compares packed string keys and returns match, overflow, or not-found state.
- `befs_btree_read()`: public ordered traversal by key ordinal. It seeks to the first leaf and walks right-linked leaf nodes until the requested key index is reached.
- `befs_btree_seekleaf()`: descends to the first leaf node, with explicit handling for empty trees and empty internal nodes.
- `befs_leafnode()`: treats nodes with invalid overflow pointer as leaves.
- Layout helpers:
  - `befs_bt_keylen_index()`
  - `befs_bt_valarray()`
  - `befs_bt_keydata()`
  - `befs_bt_get_key()`
- `befs_compare_strings()`: bytewise string comparison with length tie-break.

## Data Model
A node contains:
1. `befs_btree_nodehead`
2. packed key bytes
3. aligned `fs16` key-end-offset array
4. `fs64` value array

The code uses 8-byte alignment for the key length index, noting that documented 4-byte rounding did not work in practice.

## Limitations and Risks
- The comments state this is currently only suitable for directory B+trees: duplicate keys and non-string key types are not implemented.
- `befs_bt_get_key()` allows `index == all_key_count`, which can address one past the valid key index in malformed paths.
- `befs_find_key()` assumes node key count is nonzero before reading the last key.
- The B+tree reader relies on on-disk node integrity; it does not deeply bounds-check key length arrays against buffer size.

## Dependencies
Uses `befs_read_datastream()` for all reads, endian helpers from `endian.h`, and BeFS diagnostics from `debug.c`.
