# File Research: sources/os/linux/linux-stable/fs/ext4/verity.c

## Purpose

`verity.c` implements `fsverity_operations` for ext4. It stores fs-verity metadata, including the Merkle tree and fsverity descriptor, beyond the visible end of the file, beginning at the first 64 KiB boundary after `i_size`.

This design keeps verity metadata encrypted when file contents are encrypted, because metadata is stored as file data beyond EOF rather than as xattrs.

## Metadata Layout

- `ext4_verity_metadata_pos(inode)` returns `round_up(inode->i_size, 65536)`.
- The Merkle tree starts at that position.
- The verity descriptor starts at the next filesystem block boundary after the Merkle tree.
- The descriptor size is stored as a little-endian 32-bit value in the last 4 bytes of the last allocated filesystem block, either in the descriptor-ending block or a following block if needed.
- Ext4 later finds the descriptor by finding the last extent and reading those last 4 bytes.

## Page-Cache I/O Helpers

- `pagecache_read()` reads arbitrary bytes, including beyond `i_size`, using `read_mapping_folio()` and `memcpy_from_file_folio()`.
- `pagecache_write()` writes arbitrary bytes beyond `i_size` using the mapping's `write_begin` and `write_end` operations. It rejects writes beyond `s_maxbytes` and requires full write completion.

These helpers avoid normal VFS read/write interfaces because verity enabling may write through a read-only file descriptor and must access beyond EOF.

## Enabling Verity

`ext4_begin_enable_verity()` prepares a file for verity metadata creation:

- Rejects DAX files and inodes with DAX flag.
- Rejects concurrent verity enablement via `EXT4_STATE_VERITY_IN_PROGRESS`.
- Attaches a JBD2 inode and initializes quotas because the file was opened read-only.
- Converts inline data to normal storage.
- Requires extent-based files.
- Truncates any blocks beyond EOF so descriptor lookup cannot be confused by old post-EOF allocations.
- Adds the inode to the orphan list in a small transaction.
- Sets `EXT4_STATE_VERITY_IN_PROGRESS`.

`ext4_end_enable_verity()` completes or rolls back verity enablement:

- If `desc == NULL`, it skips straight to cleanup.
- Writes the verity descriptor using `ext4_write_verity_descriptor()`.
- Calls `filemap_write_and_wait()` to flush both normal data and verity metadata while `EXT4_STATE_VERITY_IN_PROGRESS` is still set.
- Starts a transaction, marks fast commit ineligible for verity, removes the inode from the orphan list, reserves inode write access, sets `EXT4_INODE_VERITY`, syncs inode flags, marks the inode dirty, clears the in-progress state, and returns success.
- On any error, truncates page cache back to `i_size`, truncates allocated metadata blocks, removes the orphan record if present, clears the in-progress state, and returns the error.

The orphan-list protocol protects crash consistency: incomplete verity enablement leaves cleanup work discoverable.

## Descriptor Lookup and Reads

- `ext4_get_verity_descriptor_location()` requires extent-based storage, finds the last extent with `ext4_find_extent()`, derives the last allocated logical block, reads the trailing descriptor-size field, validates size and position, and returns descriptor size and offset.
- It reports corruption when the file lacks extents, has no extents, has an impossible descriptor size, or points before the verity metadata area.
- `ext4_get_verity_descriptor()` returns descriptor size when `buf_size == 0`, or reads the descriptor into the supplied buffer after checking capacity.

## Merkle Tree Operations

- `ext4_read_merkle_tree_page()` offsets the requested page index by `ext4_verity_metadata_pos() >> PAGE_SHIFT` and calls `generic_read_merkle_tree_page()`.
- `ext4_readahead_merkle_tree()` applies the same offset and calls `generic_readahead_merkle_tree()`.
- `ext4_write_merkle_tree_block()` offsets the provided position by the metadata base and writes through `pagecache_write()`.

## Exported Operation Table

`ext4_verityops` provides:

- `.begin_enable_verity = ext4_begin_enable_verity`
- `.end_enable_verity = ext4_end_enable_verity`
- `.get_verity_descriptor = ext4_get_verity_descriptor`
- `.read_merkle_tree_page = ext4_read_merkle_tree_page`
- `.readahead_merkle_tree = ext4_readahead_merkle_tree`
- `.write_merkle_tree_block = ext4_write_merkle_tree_block`

This table is assigned to `sb->s_vop` during mount when `CONFIG_FS_VERITY` is enabled.

## Edge Cases

- DAX is rejected because fs-verity metadata is managed through page-cache paths.
- Inline data is converted before enabling verity.
- Non-extent files are rejected for verity enablement and treated as corruption if already marked verity.
- Existing post-EOF blocks are truncated before writing verity metadata to keep descriptor discovery unambiguous.
- Cleanup must remove both cached and allocated metadata beyond `i_size`.
- Descriptor location is inferred from the last allocated block, so corrupt extents or unexpected post-EOF allocations can make verity metadata unreadable and trigger ext4 corruption reporting.
