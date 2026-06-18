# File Research: sources/local-fs/jfsutils/fsck/fsckmeta.c

## Role

`fsckmeta.c` is the JFS fsck metadata validation and repair coordinator. It validates superblocks, chooses usable primary/secondary aggregate inode table data, records fixed and inode-described metadata ownership into fsck workspace maps, checks duplicate metadata block references, and repairs limited metadata structures such as the root directory inode/tree.

It depends heavily on global fsck state:

- `sb_ptr`: current superblock buffer.
- `agg_recptr`: aggregate-wide fsck state, buffers, flags, selected AIT parts, block-map state, and inode records.
- `Vol_Label`: message/device label.

## Major Responsibilities

- Superblock validation and replication:
  - `validate_repair_superblock()` reads primary superblock first, then secondary if needed.
  - `validate_super()` checks magic/version, block sizes, device size compatibility, flags, allocation group sizing, fsck workspace placement, journal placement, and secondary AIT/AIM descriptors.
  - `validate_super_2ndaryAI()` validates secondary aggregate inode map/table descriptors and cross-checks them with the alleged secondary AIT self inode and the other superblock.
  - `replicate_superblock()` writes the in-memory superblock to both primary and secondary copies, forcing dirty state if clean replication cannot be trusted.
  - `agg_clean_or_dirty()` reconciles fsck’s computed dirty state with `s_state`, updating superblocks when writable.

- Aggregate inode table selection:
  - `validate_select_agg_inode_table()` validates primary AIT part 1 and part 2, falls back to secondary, and can combine part 1 from one AIT with part 2 from the other.
  - Part 1 covers aggregate metadata inodes 0 through 15.
  - Part 2 covers aggregate fileset inodes 16 through 31, with release 1 using `FILESYSTEM_I`.
  - Selection results are stored in `agg_recptr->primary_ait_4part1` and `agg_recptr->primary_ait_4part2`.

- Metadata inode validation:
  - `verify_ait_part1()` validates aggregate self inode, block map inode, journal inode, and bad block inode.
  - `verify_ait_part2()` validates the aggregate fileset inode.
  - `verify_ait_inode()`, `verify_bmap_inode()`, `verify_log_inode()`, `verify_badblk_inode()`, and `verify_agg_fileset_inode()` perform structural inode checks, then call `verify_metadata_data()`.
  - `verify_metadata_data()` initializes the inode record, validates the inode’s B+ tree/data with `validate_data()`, compares recorded block counts and byte sizes, and backs out recorded blocks if size validation proves the tree unusable.

- Fileset metadata validation and repair:
  - `validate_fs_metadata()` verifies the fileset super extension inode when possible, then verifies/repairs the root directory inode.
  - `verify_fs_super_ext()` validates the reserved fileset extension inode but intentionally ignores its content because release 1 does not use it.
  - `verify_repair_fs_rootdir()` verifies root inode identity, mode, parent reference, EA/ACL fields, directory tree, block counts, and size. In read/write mode it can recreate or normalize root directory metadata.
  - `rootdir_tree_bad()` reinitializes the root directory to an empty valid directory tree and marks `rootdir_rebuilt`.

- Workspace ownership accounting:
  - `record_fixed_metadata()` records reserved aggregate space, primary/secondary superblocks, and phantom blocks described by the final dmap page.
  - `record_other_ait()` records the AIT/AIM copy not selected for active processing.
  - `record_ait_part1_again()` re-records verified part 1 aggregate metadata inodes after earlier backout during mixed primary/secondary selection.
  - `backout_ait_part1()` and `backout_valid_agg_inode()` remove previously recorded ownership for metadata inodes when an AIT path fails.

- Duplicate and first-reference checks:
  - `fatal_dup_check()` emits ranges for duplicate metadata block references and returns `FSCK_DUPMDBLKREF`.
  - `first_ref_check_agg_metadata()`, `first_ref_check_fs_metadata()`, `first_ref_check_fixed_metadata()`, and `first_ref_check_other_ait()` resolve duplicate-allocation first references against aggregate metadata, fileset metadata, fixed metadata, and the non-selected AIT/AIM.

## Important Control Flow

The early fsck metadata path is roughly:

1. `validate_repair_superblock()` obtains a valid superblock.
2. `validate_select_agg_inode_table()` chooses primary, secondary, or mixed AIT parts.
3. Verified metadata inodes are recorded in the workspace block map.
4. `record_fixed_metadata()` and `record_other_ait()` reserve non-inode-described metadata.
5. `validate_fs_metadata()` validates fileset super extension and root directory.
6. Duplicate and first-reference checks operate over the recorded metadata ownership.
7. `agg_clean_or_dirty()` marks final clean/dirty state.

## Data and State Mutations

This file can mutate:

- Superblock state (`sb_ptr->s_state`) and replicated on-disk superblocks.
- `agg_recptr` selection flags, dirty/modified flags, inode stamp, duplicate state, correction flags, and root rebuild flags.
- Per-inode fsck records from `get_inorecptr()`.
- On-disk root directory inode and super extension inode through `inode_put()`.
- Workspace block ownership maps through record/unrecord helpers.

## Error Handling Pattern

The file follows a conservative validation pattern:

- Validate identity fields before parsing deeper structures.
- Stop deep B+ tree validation when basic inode identity is wrong.
- Record block ownership only for validated metadata.
- Back out ownership if a later check fails.
- Treat duplicate metadata block allocation as fatal or dirty.
- In read-only mode, report and mark dirty instead of repairing.

## Notable Observations

- `verify_ait_inode()` checks `di_fileset != AGGREGATE_I` twice with different message suffixes. This looks like duplicated validation logic, possibly a historical copy/paste.
- `verify_badblk_inode()` maps invalid bad-block inode final status to `FSCK_BMINOBAD`, while `verify_ait_part1()` later maps bad-block failures to `FSCK_BBINOBAD` in some paths. This may be intentional reuse, but it is worth checking if diagnostics need to distinguish bad block inode failures.
- `validate_fs_metadata()` intentionally tolerates failures in the fileset super extension inode and proceeds to root directory validation with `goto read_root`; comments say the extension is not important enough to block root validation.
- Root directory repair is aggressive in read/write mode: if identity or tree shape is bad, the code may reinitialize it as an empty root directory, preserving fsck progress at the cost of requiring later reconnection/lost+found handling elsewhere.

## External Dependencies

Key helpers are declared or included via `xfsckint.h`, `devices.h`, `diskmap.h`, `message.h`, `super.h`, and `utilsubs.h`. This file calls many cross-module routines, including:

- Device/superblock helpers: `ujfs_get_superblk()`, `ujfs_put_superblk()`, `ujfs_get_dev_size()`.
- Inode/buffer helpers from `fsckpfs.c`: `ait_special_read_ext1()`, `inode_get()`, `inode_put()`.
- Metadata scanners: `validate_data()`, `validate_dir_data()`, `process_valid_data()`, `process_valid_dir_data()`.
- Workspace map helpers: `blkall_increment_owners()`, `blkall_ref_check()`, `record_valid_inode()`, `unrecord_valid_inode()`, `first_ref_check_inode()`.
- EA/ACL helpers: `validate_EA()`, `validate_ACL()`, `clear_EA_field()`, `clear_ACL_field()`.
- Messaging: `fsck_send_msg()` and `fsck_ref_msg()`.
