# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_dir_idx.c

Ext4 htree indexed directory implementation. It initializes indexed directories, computes hashes, verifies and updates htree checksums, searches htree nodes, handles hash collision continuation, splits full data blocks, splits/grows index nodes, inserts entries, and updates `..` for indexed directory renames.

Key behavior:
- Inline accessors wrap htree root info, count/limit, entry hash, and child block fields with little-endian conversion.
- `ext4_dir_dx_checksum`, `ext4_dir_dx_csum_verify`, and `ext4_dir_set_dx_csum` implement htree node checksum support using filesystem UUID seed, inode number, generation, entries, and tail.
- `ext4_dir_dx_init` creates root block entries for `.` and `..`, initializes htree metadata, appends the first leaf block, and links it from the root.
- `ext4_dir_hinfo_init` validates root htree metadata, selects signed/unsigned hash variant, loads hash seed, and computes the target name hash.
- `ext4_dir_dx_get_leaf` descends the htree using binary search through index entries and loads child blocks.
- `ext4_dir_dx_find_entry` locates the candidate leaf, linearly searches it, then follows collision-continuation blocks when needed.
- `ext4_dir_dx_split_data` sorts existing leaf dirents by hash, splits them into old/new leaf blocks, initializes checksum tails, and inserts a new htree entry.
- `ext4_dir_dx_split_index` handles root-to-node growth and internal node splits within the ext4 htree height limit used by Linux.
- `ext4_dir_dx_add_entry` combines leaf lookup, index split, direct insertion, data split, and final insertion of the new name.
- `ext4_dir_dx_reset_parent_inode` rewrites the `..` inode in an indexed directory root block.

Notable dependencies:
- Hashing from `ext4_hash.c`/`ext4_hash.h`.
- Directory block operations from `ext4_dir.c`.
- Block mapping/appending from `ext4_fs.c`.
- Checksums from `ext4_crc32.c`.

Research notes:
- Root checksum mismatch paths in `ext4_dir_dx_find_entry` and `ext4_dir_dx_add_entry` return before releasing `root_block`, which can leak a cache reference.
- Several htree checksum mismatch paths treat child/root corruption as hard errors, while lower-level descent may only warn for some internal blocks.
- The implementation supports only htree depth 0 or 1, matching the hardcoded two-block path array and Linux limit noted in comments.
- `ext4_dir_dx_split_data` assumes a valid sortable set of entries; edge cases with no entries or pathological hashes would rely on assertions or surrounding directory invariants.
