# File Research: sources/local-fs/e2fsprogs/e2fsck/pass2.c

## Purpose

`pass2.c` implements e2fsck pass 2: directory structure checking. It iterates active directory blocks collected in pass 1 and validates each directory entry. It also collects parent relationships for subdirectories, computes inode reference counts, validates indexed-directory htrees, and frees several pass-1 data structures when finished.

## Main Entry Points

- `e2fsck_pass2(e2fsck_t ctx)`: orchestrates directory checking.
- `e2fsck_process_bad_inode(...)`: repairs or clears inodes that pass 1 marked as having bad fields.
- Internal helpers include `check_dir_block`, `check_dot`, `check_dotdot`, `check_filetype`, `parse_int_node`, `salvage_directory`, `allocate_dir_block`, `deallocate_inode`, and `clear_htree`.

## Top-Level Flow

`e2fsck_pass2` creates `ctx->inode_count` from pass-1 link hints, allocates a two-block directory scan buffer, sets root's parent to itself, prepares readahead state, sorts the directory block list specially when directory indexing is enabled, and iterates `fs->dblist`.

After directory scanning, it walks all collected `dx_dir_info` records to validate htree parent/child references, hash bounds, duplicate references, depth, and unreferenced blocks. Bad htrees can have `EXT2_INDEX_FL` cleared and be scheduled for rehash.

The pass then frees:

- `fs->dblist`
- `inode_bad_map`
- `inode_reg_map`
- `inode_casefold_map`
- encrypted file info
- casefolded directory list

It also sets the large-file feature if pass 1 observed large regular files.

## Directory Entry Validation

`check_dir_block` is the core scanner. For each directory block or inline-data segment, it:

- reads directory data, tolerating and later repairing checksum/corruption errors
- creates a missing block when directory block zero is absent and appropriate
- handles inline-data directory layout and bad inline-data sizes
- initializes htree block state when the directory is indexed
- handles missing checksum tails and schedules rehash when necessary
- loops through dirents by `rec_len`, validating bounds, minimum size, alignment, and name storage
- repairs corrupt dirent layout through `salvage_directory`
- validates first `.` entry through `check_dot`
- validates second `..` entry through `check_dotdot`, recording the dotdot target in dirinfo
- removes later duplicate `.` or `..` entries
- rejects illegal inode numbers, quota/orphan special inodes, root hardlinks, null names, EA inode links, and references to bad-block-table inodes
- calls `e2fsck_process_bad_inode` for inode_bad_map entries
- detects references to uninitialized inode-table groups and requests restart after clearing bad group metadata
- clears references to unused inodes unless a restart is pending
- fixes dirent file type fields
- validates encrypted directory names and encryption policy inheritance
- validates casefolded/encoded names when strict or requested
- tracks htree hash min/max values
- sets parent pointers for child directories and detects illegal directory hard links
- detects duplicate filenames with a dictionary and schedules rehash
- increments `ctx->inode_count`, link statistics, and total directory-entry count

Modified directory blocks are written back through either `ext2fs_inline_data_set` or `ext2fs_write_dir_block4`.

## HTree Handling

The file validates both root/internal htree nodes and leaf hash ranges:

- `special_dir_block_cmp` ensures logical block zero is processed before other blocks.
- `parse_int_node` verifies count/limit fields, checksum errors, block references, hash ordering, duplicate references, parent links, node min/max hashes, and first/last flags.
- `update_parents` propagates min/max hash boundaries upward.
- `htree_depth` computes depth for validation.
- `clear_htree` clears `EXT2_INDEX_FL` and schedules directory rehash if possible.

## Inline, Encryption, and Casefold Support

Inline directories are treated as synthetic directory blocks: the `.` and `..` entries may be fabricated for validation, and the EA-backed second segment is checked when present. Encrypted directories require encrypted names of adequate size and matching policy IDs for regular files, directories, and symlinks. Casefolded directories use encoding-aware comparison for duplicate-name detection and encoded-name validation.

## Bad Inode Repair

`e2fsck_process_bad_inode` rereads a bad inode and fixes bad ACL blocks, invalid modes, invalid special files, invalid symlinks, nonzero fragment fields, high block count fields without huge_file, high ACL fields without 64bit, invalid ACL block numbers, and inappropriate directory high-size fields. If an inode must be cleared, `deallocate_inode` reverses in-memory allocation/quota state before calling `e2fsck_clear_inode`.

## Risk and Test Focus

Important edge cases include inline directories, metadata checksum tails, htree hash bounds, directory duplicate-name handling under casefolding, encrypted directory policy mismatch, group descriptor `INODE_UNINIT` repair and restart, and clearing bad inodes without double-counting quota/block state.
