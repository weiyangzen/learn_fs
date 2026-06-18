# File Research: sources/os/linux/linux/fs/ecryptfs/mmap.c

Defines eCryptfs address-space operations for encrypted/decrypted page-cache I/O.

Key behavior:
- `ecryptfs_writepages()` iterates writeback folios, encrypts each folio with `ecryptfs_encrypt_page()`, records mapping errors, and unlocks folios.
- Handles “view as encrypted” reads, including reconstructing an encrypted header view when metadata is stored in xattrs.
- `ecryptfs_read_folio()` chooses plain lower reads, encrypted-view reads, or decryption based on crypt-stat flags.
- `ecryptfs_write_begin()` prepares a folio, reads/decrypts lower content when needed, and fills holes by truncating/zeroing.
- `ecryptfs_write_end()` writes unencrypted passthrough data directly or encrypts the folio, updates upper size, and writes the size back to metadata.
- Writes plaintext inode size either to the lower file header or to the eCryptfs xattr.
- Provides `ecryptfs_bmap()` by forwarding to the lower inode `bmap()`.
- Exports `ecryptfs_aops` with read, write, writepages, migration, invalidation, dirty-folio, and bmap hooks.

Important interactions:
- Uses `ecryptfs_xattr_cache` for xattr metadata updates.
- Calls lower I/O helpers from `read_write.c`.
- Crypt-stat flags control whether data is passed through, decrypted, encrypted, exposed as encrypted, or metadata-backed by xattrs.
