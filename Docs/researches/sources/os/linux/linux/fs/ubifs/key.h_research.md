# File Research: sources/os/linux/linux/fs/ubifs/key.h

## Purpose

`key.h` defines UBIFS key format helpers. UBIFS currently uses the simple 64-bit key format, but most helpers accept `struct ubifs_info *c` to preserve an abstraction boundary for possible future key formats. The simple key stores inode number in the first 32 bits and key type plus block/hash payload in the second 32 bits.

## Hash Helpers

`key_mask_hash()` masks hash values to the simple-key hash field and avoids reserved readdir offsets 0, 1, and 2. `key_r5_hash()` implements the ReiserFS-derived R5 name hash. `key_test_hash()` copies up to four name bytes into a hash value for testing. Directory and xattr entry key initialization uses `c->key_hash`, so the selected hash function is filesystem state.

## Key Constructors

The header provides constructors for all logical UBIFS key classes. `ino_key_init()` and `ino_key_init_flash()` create inode keys. `lowest_ino_key()` and `highest_ino_key()` define search bounds for all keys belonging to an inode.

`dent_key_init()`, `dent_key_init_hash()`, and `dent_key_init_flash()` create directory-entry keys using parent inode plus name hash. `lowest_dent_key()` defines the lower bound for scanning a directory's dentries. `xent_key_init()`, `xent_key_init_flash()`, and `lowest_xent_key()` do the same for extended attribute entries hosted by an inode.

`data_key_init()` creates a data key from inode number and UBIFS block number; `highest_data_key()` creates the upper data-key bound for an inode. `trun_key_init()` creates replay-only truncation keys, and `invalid_key_init()` writes a sentinel invalid key.

Flash constructors write little-endian fields and clear unused bytes up to `UBIFS_MAX_KEY_LEN`. In-memory constructors write host-endian `u32` fields.

## Accessors and Conversion

`key_type()` and `key_type_flash()` extract key type. `key_inum()` and `key_inum_flash()` extract inode numbers. `key_hash()` and `key_hash_flash()` return dent/xent hash payloads. `key_block()` and `key_block_flash()` return data block numbers.

`key_read()` converts an on-flash little-endian key to in-memory format. `key_write()` converts in-memory to flash format and clears unused key bytes. `key_write_idx()` writes the compact index form without clearing bytes beyond the key fields. `key_copy()` copies the full 64-bit key value.

## Comparison and Limits

`keys_cmp()` compares inode field first and payload/type field second, matching the sorted TNC key order. `keys_eq()` tests exact equality. `is_hash_key()` identifies dent/xent keys, which can collide and require name-aware handling. `key_max_inode_size()` derives the maximum file size representable by the active key format; for simple keys it is the block-key space multiplied by `UBIFS_BLOCK_SIZE`.

## Consumers

The journal, GC, TNC, replay, xattr, and directory code all depend on these helpers for consistent key construction. Bugs here would affect lookup ordering, collision handling, flash compatibility, and range deletion.
