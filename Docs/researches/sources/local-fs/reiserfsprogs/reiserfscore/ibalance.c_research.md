# File Research: sources/local-fs/reiserfsprogs/reiserfscore/ibalance.c

## Purpose
`ibalance.c` executes internal-node balancing plans computed by `fix_node.c`. It mutates internal node key arrays and disk-child pointer arrays for shifts, merges, splits, inserts, deletes, root creation, and root collapse.

## Main Responsibilities
- Copies, inserts, deletes, and moves internal node keys and child pointers.
- Shifts child pointers between `S[h]`, `L[h]`, and `R[h]`.
- Updates delimiting keys in common parents.
- Handles borrowing/merging after deletion.
- Creates a new root when the tree grows.
- Replaces the root and decrements tree height when the old root becomes empty.
- Returns promoted split keys and new child pointers to the next level.

## Key Functions
- `internal_define_dest_src_infos()` maps shift modes to source/destination `buffer_info`, common parent, and delimiting key index.
- `internal_insert_childs()` inserts child pointers and keys into an internal node and updates child-size accounting in the parent.
- `internal_delete_pointers_items()` and `internal_delete_childs()` remove internal pointers/keys and adjust free space.
- `internal_copy_pointers_items()` and `internal_move_pointers_items()` copy/move fixed-size internal records between nodes.
- `internal_shift_left()`, `internal_shift1_left()`, `internal_shift_right()`, and `internal_shift1_right()` implement the concrete left/right transfer operations.
- `balance_internal_when_delete()` executes deletion-specific plans, including root shrink and neighbor borrow/merge.
- `replace_lkey()` and `replace_rkey()` update delimiting keys after leaf/internal boundary changes.
- `balance_internal()` is the public executor for one internal level.

## Data and Control Flow
`balance_internal()` interprets `tb->insert_size[h]` as a count of inserted or deleted internal units. Negative values dispatch to `balance_internal_when_delete()`. Positive values apply any planned left shift, right shift, split, or root creation before inserting remaining keys and child pointers into the current node.

If `tb->blknum[h] == 2`, it obtains an FEB buffer for `S_new`, moves roughly half of `S[h]` into it, and prepares `new_insert_key`/`new_insert_ptr` for the parent level. If no `S[h]` exists, it creates a new root from an FEB buffer and updates the superblock root block and tree height.

## Integration Points
- Consumes `tree_balance` fields filled by `fix_node.c`.
- Uses `buffer_info` helpers and buffer dirtying primitives.
- Uses `replace_key()`, `reiserfs_invalidate_buffer()`, `get_FEB()`, and superblock accessors.
- Feeds promoted keys/pointers back to the caller, normally higher-level balance orchestration.

## Risks and Edge Cases
- All data movement uses raw `memmove`/`memcpy` over packed on-disk arrays; off-by-one errors corrupt tree shape.
- Deletion uses negative `lnum`/`rnum` to mean borrowing from neighbors, while other signs mean shifts/joins. The sign convention is critical.
- New root creation writes into `PATH_OFFSET_PBUFFER(..., ILLEGAL_PATH_ELEMENT_OFFSET)`, so path layout assumptions must match header macros.
- Parent child-size accounting must remain synchronized with internal free space or later planning becomes wrong.

## Testing Signals
Tests should trigger internal left/right shifts, borrow from left/right, merge with left/right, split into `S_new`, create root, collapse root, and insert at boundary positions including `child_pos == -1`.
