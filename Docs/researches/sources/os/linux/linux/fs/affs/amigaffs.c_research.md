# File Research: sources/os/linux/linux/fs/affs/amigaffs.c

Implements AFFS on-disk structure helpers: hash chains, link removal, checksums, date/protection conversion, error reporting, and name validation.

Key behavior:
- `affs_insert_hash()` inserts a file header block into a directory hash chain:
  - Hashes the name.
  - Traverses the hash chain to the end.
  - Sets parent/hash-chain fields.
  - Fixes checksums and dirties directory metadata.
  - Updates directory mtime/ctime and inode version.
- `affs_remove_hash()` removes a header block from its directory hash chain and patches either the hash table slot or previous entry’s hash-chain pointer.
- `affs_fix_dcache()` updates alias dentry `d_fsdata` when a hardlink block is replaced by the inode’s main block.
- `affs_remove_link()` removes an AFFS hardlink block:
  - If removing the head entry, promotes the first link by copying its name/hash position.
  - Unlinks the link-chain entry.
  - Frees the removed link block.
  - Adjusts nlink when appropriate.
- `affs_empty_dir()` checks whether a directory hash table contains any children.
- `affs_remove_header()` removes a filesystem object:
  - Locks link and directory state.
  - Verifies directories are empty.
  - Removes from parent hash.
  - Removes a hardlink or clears nlink.
  - Marks inode ctime/dirty.
- `affs_checksum_block()` sums big-endian 32-bit words.
- `affs_fix_checksum()` recomputes the header checksum field.
- `affs_secs_to_datestamp()` converts Unix seconds to Amiga days/minutes/ticks, applying timezone and epoch delta.
- `affs_prot_to_mode()` maps Amiga protection bits to Linux permissions.
- `affs_mode_to_prot()` maps Linux permissions back to Amiga protection bits, handling inverted owner bits and MUFS group/other bits.
- `affs_error()` logs critical errors and remounts the filesystem read-only.
- `affs_warning()` logs nonfatal warnings.
- `affs_check_name()` validates AFFS names, optionally enforcing no truncation beyond 30 bytes.
- `affs_copy_name()` writes a length-prefixed AFFS name.

Important interactions:
- Hash/link logic is called by namei operations.
- Bitmap block freeing is delegated to `bitmap.c`.
- Error handling can force the whole mounted filesystem read-only.
