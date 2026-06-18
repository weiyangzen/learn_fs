# File Research: sources/local-fs/jfsutils/fsck/fsckino.c

## Purpose
Implements per-fileset-inode fsck validation and repair helpers. It validates EA, ACL, file data, directory data, inline inode storage layout, inode sizes and block counts; records/unrecords valid inode-owned extents; releases bad inodes; clears corrupt EA/ACL descriptors; checks duplicate-allocation first references; and builds/display paths for inode diagnostics.

## Main Elements
- EA/ACL cleanup:
  - `backout_EA()` and `backout_ACL()` unrecord out-of-line EA/ACL extents from fsck workspace maps and decrement inode/fileset running totals.
  - `clear_EA_field()` and `clear_ACL_field()` unrecord eligible EA/ACL extents, update block counters, and zero descriptor length/address fields.
- Path reporting:
  - `get_path()` walks upward from an inode and parent directory by repeatedly calling `direntry_get_objnam()`, converting Unicode names to UTF-8, and assembling a path backward in `agg_recptr->path_buffer`.
  - `display_path()` emits type-specific path messages and distinguishes expected vs illegal hard-link parents for directories.
  - `display_paths()` emits all observed paths, using parent extension records when multiple parents were recorded.
- Duplicate-allocation first-reference queries:
  - `first_ref_check_inode()` queries EA, ACL, and validated data extents with `process_extent(..., FSCK_QUERY)` or valid-data helpers.
- Inline layout and inode identity:
  - `in_inode_data_check()` verifies that inline data, inline EA, and inline ACL descriptions do not overlap inode storage.
  - `inode_is_in_use()` checks inode stamp, number, fileset, inode-table PXD, and nonzero link count.
  - `parent_count()` counts the primary parent plus parent extension records.
- Valid-inode recording:
  - `record_valid_inode()` records already-validated EA/ACL extents and data extents.
  - `unrecord_valid_inode()` reverses recording for EA/ACL and directory/file data.
  - `release_inode()` sets `di_nlink` to zero on disk and unrecords valid blocks when they are trusted.
- Descriptor/data validation:
  - `validate_EA()` validates EA DXD flags, inline bounds, extent size bounds, extent allocation, reads out-of-line EA data when small enough, and validates FEALIST format via `jfs_ValidateFEAList()`.
  - `validate_ACL()` validates ACL DXD flags and inline/extent bounds, then records extent-backed ACL blocks.
  - `validate_data()` validates non-directory regular-file/symlink data rooted in an xtree, with special handling for short inline symlinks.
  - `validate_dir_data()` validates directory dTree data and, when directory indexing is enabled, the directory table xtree; it schedules index-table rebuild when the xtree is bad but the dTree can still be used.
  - `validate_record_fileset_inode()` is the main orchestrator for one in-use fileset inode.

## Control Flow
The normal per-inode path is `inode_is_in_use()` followed by `validate_record_fileset_inode()`. The validator creates or fetches the fsck inode record, marks it in use, classifies the inode type, subtracts the on-disk link count from the fsck link-count accumulator, then validates EA, ACL, and object data.

For regular files and long symlinks, `validate_data()` checks that `di_dxd` is an xtree root and calls `xTree_processing(..., FSCK_RECORD_DUPCHECK)`. If the tree is corrupt, it marks the inode for release, backs out recorded tree/EA/ACL extents when possible, and uses fatal metadata return codes for metadata inodes.

For directories, `validate_dir_data()` first handles optional directory-index xtree validation, then runs `dTree_processing(..., FSCK_RECORD_DUPCHECK)`. If dTree validation fails, it unre records dTree extents and backs out EA/ACL extents. If the directory index tree is bad but the dTree is usable, it clears index checking, marks `rebuild_dirtable`, unre records the directory-table xtree, and fixes `di_nblocks` to the observed valid block count.

After structure validation, `validate_record_fileset_inode()` checks `di_nblocks` against `agg_recptr->this_inode.all_blks`, checks non-directory byte size against allocated data capacity, verifies inline storage overlap, schedules INLINEEA mode-bit corrections, and updates global EA/ACL/file/directory block totals for keepers.

## Dependencies And Integration
The file depends on `xfsckint.h`, JFS byte-order and Unicode helpers, globals `sb_ptr`, `agg_recptr`, `Uni_Name`, and `Str_Name`; extent processing (`process_extent()`, `extent_record()`); data processors (`process_valid_data()`, `process_valid_dir_data()`, `xTree_processing()`, `dTree_processing()`); EA I/O and validation (`ea_get()`, `jfs_ValidateFEAList()`); inode access (`inode_get()`, `inode_put()`, `get_inorecptr()`); directory lookup (`direntry_get_objnam()`); and fsck message emission.

External callers include `xchkdsk.c` for the main fileset inode scan, path reporting, first-reference checks, inode release, and EA/ACL clearing. `fsckmeta.c` also uses the valid-inode record/unrecord and first-reference helpers for metadata inode handling.

## Behavioral Notes
EA and ACL extent blocks count toward inode/fileset allocation totals but are excluded from file/directory object data totals. Short symlinks are treated as inline data with an extra null terminator not counted in `di_size`.

Directories are not subjected to the same `di_size` capacity check used for regular files and symlinks. Directory consistency is driven primarily by dTree validation and directory-index handling.

`validate_dir_data()` forcibly sets `DXD_INDEX` on directory data roots as a workaround for an older bug that could clear the bit. This mutates the in-memory inode before checking the root flags.

`clear_EA_field()` clears the EA flag to zero, while `clear_ACL_field()` sets the ACL flag to `DXD_CORRUPT` with zero length/address. That asymmetry is visible in the code and matters to later repair interpretation.

## Risk Notes
The highest-risk behavior is counter and block-map rollback after late validation failure. If a tree appears valid until a block-count or size check fails, the code must unrecord EA, ACL, and data extents in the same shape they were recorded.

The tree-corruption rollback paths back out ACL only inside the `!ignore_ea_blks` branch, so EA/ACL ignore-state combinations are delicate. Directory-index rebuild handling is also fragile because it temporarily restores `ignore_alloc_blks` to the xtree result before unrecording directory-table extents.

Path construction depends on parent records and directory entries still being usable; disconnected or selected-for-release parents intentionally produce partial paths rather than rooted paths.
