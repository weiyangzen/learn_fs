# File Research: sources/os/linux/linux-stable/fs/ecryptfs/mmap.c

## Summary
Provides eCryptfs address-space operations for reading, writing, encrypting, decrypting, and syncing inode size metadata.

## Main Responsibilities
- Encrypts dirty folios during writeback.
- Reads lower data and decrypts it unless encrypted-view mode is active.
- Synthesizes encrypted-view headers when metadata lives in xattrs.
- Implements write begin/end behavior and hole zeroing.
- Writes logical file size to either the lower file header or metadata xattr.

## Key APIs
- `ecryptfs_write_inode_size_to_metadata()`
- `ecryptfs_aops`

## Important Behavior
`read_folio()` chooses between passthrough lower read, encrypted-view copy-up, or decryption. `write_begin()` prepares missing or partial pages, fills holes through truncate, and handles encrypted-view data. `write_end()` encrypts completed pages and updates encrypted metadata size.

## Risks
This file has delicate ordering around folio uptodate state, lower inode size, encrypted metadata, and xattr writes. The address-space ops still use block dirty/invalidate hooks under `CONFIG_BLOCK`, with an in-file warning that this is a compatibility compromise.
