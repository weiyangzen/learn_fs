# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_dir.c

Directory entry manipulation and linear directory iteration/search/add/remove support. It also handles ext4 directory entry checksum tails and delegates to htree indexing when directory indexes are enabled.

Key behavior:
- `ext4_dir_csum_verify`, `ext4_dir_set_csum`, and tail helpers validate and update metadata checksum directory tails.
- `ext4_dir_iterator_init`, `ext4_dir_iterator_next`, and `ext4_dir_iterator_fini` walk directory entries across inode data blocks, validating alignment, record length, and name length.
- `ext4_dir_write_entry` writes an ext4 dirent with inode number, record length, name length, file type, and name bytes.
- `ext4_dir_add_entry` uses htree insertion if `dir_index` and inode index flag are present; otherwise it searches linear blocks for space or appends a new data block.
- `ext4_dir_find_entry` uses htree lookup when available, otherwise scans all directory data blocks linearly.
- `ext4_dir_remove_entry` invalidates an entry, merges its record length into the previous entry when possible, updates checksum, and marks the block dirty.
- `ext4_dir_try_insert_entry` inserts into an invalid entry or splits slack from a valid entry.
- `ext4_dir_find_in_block` performs name-length-first matching inside a single directory block.

Notable dependencies:
- Htree implementation in `ext4_dir_idx.c`.
- Data block mapping via `ext4_fs_get_inode_dblk_idx` and appending via `ext4_fs_append_inode_dblk`.
- Transaction block access and dirty marking through `ext4_trans`.

Research notes:
- Checksum failures on linear leaf blocks are logged as warnings and do not stop lookup/add in most paths.
- `ext4_dir_iterator_next` skips inode-zero entries but assumes `it->curr` is valid on entry.
- The fallback for unsupported file types writes `EXT4_DE_UNKNOWN`.
- Directory insertion with metadata checksums reserves space for `ext4_dir_entry_tail` in new blocks.
