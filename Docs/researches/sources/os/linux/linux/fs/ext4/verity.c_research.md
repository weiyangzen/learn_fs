# File Research: sources/os/linux/linux/fs/ext4/verity.c

## Purpose
Implements ext4’s `fsverity_operations`, storing fs-verity Merkle tree and descriptor metadata beyond EOF while preserving encryption and crash-consistency requirements.

## Main Elements
- `ext4_verity_metadata_pos()`: places verity metadata at the first 64 KiB boundary after `i_size`.
- `pagecache_read()` / `pagecache_write()`: internal reads/writes that can access metadata beyond `i_size`, unlike normal VFS file reads/writes.
- `ext4_begin_enable_verity()`: rejects DAX and concurrent verity enablement, attaches jbd2 inode/quota state, converts inline data, requires extent-based files, truncates post-EOF blocks, and adds the inode to the orphan list.
- `ext4_write_verity_descriptor()`: writes the descriptor after the Merkle tree on a filesystem block boundary and stores descriptor size in the last four bytes of the last allocated block.
- `ext4_end_enable_verity()`: writes descriptor, waits for all data and metadata writeback, marks fast commit ineligible, removes the orphan entry, sets `EXT4_INODE_VERITY`, and cleans up on failure.
- Descriptor lookup: `ext4_get_verity_descriptor_location()` finds the last extent, reads descriptor size, validates descriptor position, and reports corruption when layout is invalid.
- Merkle tree operations: offset fs-verity page/block indexes by the metadata start before delegating to generic read/readahead or internal write.
- `ext4_verityops`: operation table wired into `super.c` when `CONFIG_FS_VERITY` is enabled.

## Dependencies And Integration
Uses ext4 extents, journaling, orphan handling, quota initialization, inline-data conversion, filemap writeback, and generic fs-verity Merkle tree helpers. It is registered through `sb->s_vop` during mount.

## Behavioral Notes
Ext4 stores verity metadata beyond EOF so userspace cannot see it through normal file reads, while encrypted files still encrypt the metadata because it lives in file contents rather than xattrs. Orphan-list tracking makes interrupted enablement recoverable: unfinished metadata past EOF can be truncated during cleanup.

## Risk Notes
Descriptor discovery depends on the last allocated extent, so `ext4_begin_enable_verity()` first removes unrelated post-EOF blocks. Crash consistency depends on writing all pages before clearing the in-progress state and before persisting the verity inode flag. Corrupt extent layout or descriptor-size data is treated as filesystem corruption.
