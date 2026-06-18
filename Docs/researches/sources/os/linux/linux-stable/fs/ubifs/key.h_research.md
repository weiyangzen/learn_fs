# File Research: sources/os/linux/linux-stable/fs/ubifs/key.h

## Role

Defines UBIFS key encoding helpers. UBIFS accesses key fields through these helpers so the implementation can support alternate key formats, although this tree currently uses the simple 64-bit key format.

## Simple Key Format

The simple key format uses 64 bits:

- First 32 bits: inode number, or parent/host inode number for dent/xent keys.
- Next type bits: UBIFS key type.
- Remaining 29 bits: data block number for data keys, or hash value for directory/xattr entry keys.

Directory hash values reserve `0`, `1`, and `2` for `"."`, `".."`, and end-of-readdir style markers. `key_mask_hash()` masks and shifts reserved results away.

## Hash Helpers

`key_r5_hash()` implements the default R5 hash borrowed from ReiserFS.

`key_test_hash()` provides a testing hash based on the first four bytes of the name.

Both pass through `key_mask_hash()`.

## Key Constructors

The header provides constructors for in-memory and on-flash keys:

- Inode keys: `ino_key_init()`, `ino_key_init_flash()`
- Lowest/highest inode key ranges: `lowest_ino_key()`, `highest_ino_key()`
- Directory entry keys: `dent_key_init()`, `dent_key_init_hash()`, `dent_key_init_flash()`, `lowest_dent_key()`
- Extended attribute entry keys: `xent_key_init()`, `xent_key_init_flash()`, `lowest_xent_key()`
- Data keys: `data_key_init()`, `highest_data_key()`
- Replay-only truncation keys: `trun_key_init()`
- Invalid sentinel keys: `invalid_key_init()`

On-flash key writers use little-endian fields and clear unused bytes up to `UBIFS_MAX_KEY_LEN`.

## Key Access and Comparison

Helpers extract type, inode number, hash, and block number from memory or flash formatted keys:

- `key_type()`, `key_type_flash()`
- `key_inum()`, `key_inum_flash()`
- `key_hash()`, `key_hash_flash()`
- `key_block()`, `key_block_flash()`

`key_read()`, `key_write()`, and `key_write_idx()` convert between CPU and flash formats. `key_copy()`, `keys_cmp()`, and `keys_eq()` implement basic manipulation and ordering.

`is_hash_key()` identifies dent/xent keys that may require collision handling.

`key_max_inode_size()` derives maximum file size from the key format.

## Research Notes

This header is a central dependency for TNC lookups, journal packing, GC sorting, lprops debug validation, replay, and directory/xattr operations. Its simple ordering by inode then typed low bits is what lets UBIFS express efficient key ranges such as “all nodes for this inode.”
