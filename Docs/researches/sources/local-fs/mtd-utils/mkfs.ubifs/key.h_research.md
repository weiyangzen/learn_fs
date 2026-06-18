# File Research: sources/local-fs/mtd-utils/mkfs.ubifs/key.h

## Purpose
Provides UBIFS key construction, hashing, serialization, and comparison helpers for the simple 64-bit key scheme used by mkfs.ubifs.

## Main Helpers
- `key_mask_hash()` masks directory-entry hashes and avoids reserved values for `.`, `..`, and end-of-readdir.
- `key_r5_hash()` implements the ReiserFS-derived R5 name hash.
- `key_test_hash()` creates a predictable test hash from up to four name bytes.
- `ino_key_init()`, `dent_key_init()`, and `data_key_init()` build inode, direntry, and data keys.
- `key_write()` and `key_write_idx()` serialize in-memory keys to little-endian on-media form.
- `keys_cmp()` compares two UBIFS keys lexicographically.

## Dependencies
Relies on UBIFS constants and types from `mkfs.ubifs.h`/included headers, endian helpers from `defs.h`, and `struct qstr`.

## Risks and Notes
`key_r5_hash()` accepts a length parameter but walks until NUL rather than using `len`; callers must pass NUL-terminated names for that hash mode. `key_write()` zero-fills the unused part of the maximum key length, while `key_write_idx()` writes only the active 64-bit key.
