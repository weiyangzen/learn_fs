# File Research: sources/local-fs/btrfs-progs/check/mode-common.h

## Scope

This header declares shared state, task/progress structures, utility predicates, and repair/check helpers used by both Btrfs check modes.

## Public APIs And Data Structures

- `struct node_refs` caches bytenr/ref/check/full-backref state per B-tree level for shared-node traversal.
- `enum task_position` and `struct task_ctx` track fsck progress phases and item counts.
- Declares global accounting and control state: bytes used, csum bytes, btree bytes, fs/extent tree bytes, data allocated/referenced, duplicate/delete lists, `no_holes`, `init_extent_tree`, `check_data_csum`, `gfs_info`, and `roots_info_cache`.
- `imode_to_type()` maps POSIX inode modes to Btrfs dir-entry file types.
- `fs_root_objectid()` identifies subvolume/data-reloc/tree-reloc roots.
- Declares shared repair/check functions implemented in `mode-common.c`.
- `is_valid_imode()` validates file-type bits and rejects unused mode bits.
- `btrfs_check_subpage_eb_alignment()` warns about tree blocks not aligned to nodesize.

## Dependencies

- Uses Btrfs tree constants, access types, list helpers, and message helpers.
- Couples check modes to global fsck options and Btrfs transaction/root/path APIs.

## Risks And Invariants

- `node_refs` is central to avoiding repeated shared-tree checks and deciding full-backref expectations.
- `imode_to_type()` assumes valid `S_IFMT` bits; invalid modes are filtered separately by `is_valid_imode()`.
- Subpage alignment warnings are conservative because the checker cannot know every future page size.
