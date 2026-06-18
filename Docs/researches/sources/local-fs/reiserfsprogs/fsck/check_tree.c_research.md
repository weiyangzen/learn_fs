# File Research: sources/local-fs/reiserfsprogs/fsck/check_tree.c

Core tree-consistency checker for `reiserfsck --check`, `--fix-fixable`, and auto checks.

Main entry point:
- `check_fs_tree(fs)`

Core algorithm:
- Builds a `control_bitmap` representing blocks legitimately used by metadata, journal/reserved area, bad blocks, tree nodes, and unformatted data pointers.
- Copies the on-disk bitmap into `source_bitmap`.
- Walks the internal tree with `pass_through_tree`.
- Validates every internal node, leaf, item, item order, delimiter key, child size, and block pointer.
- Compares reconstructed usage against on-disk bitmap and superblock free-block count.

Validation coverage:
- Internal node key order and child block legality.
- Leaf structure through `leaf_structure_check`.
- Item flags and key-format consistency.
- Bad-block list item structure and pointers.
- Safe-link item patterns.
- Stat-data objectid allocation/sharing.
- Indirect item length and unformatted pointers.
- Directory item entry counts, locations, name lengths, hash order, and visible state.
- Neighbor item ordering and allowed per-file sequences.
- Left/right delimiting keys and parent child-size accounting.

Fixable actions in `FSCK_FIX_FIXABLE`:
- Clean item-header flags.
- Correct item key format.
- Zero bad indirect/badblock pointers.
- Normalize directory-entry state.
- Correct internal child-size fields.
- Merge control bitmap usage into source bitmap and update superblock free count.

Fatal conditions generally require `--rebuild-tree`.

Additional entry point:
- `do_clean_attributes(fs)`: clears v2 stat-data attribute fields across leaves and marks the superblock `reiserfs_attrs_cleared`.

Notable quirks:
- Some historical relocation/fix helpers are disabled.
- A log call in the wrong-key error path appears to pass block/item arguments in swapped order.
