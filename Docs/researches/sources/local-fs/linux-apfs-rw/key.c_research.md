# File Research: sources/local-fs/linux-apfs-rw/key.c

## Purpose
Parses APFS on-disk b-tree keys into the module’s generic `struct apfs_key` representation and implements key and filename comparison behavior.

## Main Responsibilities
- Compares normalized/case-folded APFS filenames when the volume is normalization-insensitive.
- Compares generic APFS keys by object ID, type, numeric discriminator, and optional name.
- Parses catalog keys for directory records, xattrs, file extents, sibling links, inode-like records, and other catalog entries.
- Parses non-catalog tree keys: file extent tree, spaceman free queue, omap, extent reference, snapshot metadata/name, and omap snapshot keys.
- Builds in-memory directory-record query keys, including APFS normalized-name CRC32C hash calculation.

## Key Functions
- `apfs_filename_cmp()`: compares names directly or through APFS Unicode normalization/case folding.
- `apfs_keycmp()`: provides the ordering used by node and b-tree searches.
- `apfs_read_cat_key()`: validates and decodes catalog keys, including NULL-terminated variable-length names.
- `apfs_read_*_key()`: decodes fixed-size keys for APFS auxiliary trees.
- `apfs_init_drec_key()`: initializes directory lookup keys, using name hash for normalization-insensitive volumes.

## Dependencies
Depends on `apfs.h` on-disk structures, APFS volume flags, CRC32C, and `unicode.c` cursor/normalization helpers.

## Notes
Directory key comparisons intentionally ignore normalization at `apfs_keycmp()` level; normalization-sensitive lookup is handled by hashed key construction and dentry/name comparison.
