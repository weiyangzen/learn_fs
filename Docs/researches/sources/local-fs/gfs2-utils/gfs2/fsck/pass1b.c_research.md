# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/pass1b.c

## Purpose
Implements pass 1b duplicate-block resolution. It rescans inodes to find all references to blocks pass1 marked duplicate, classifies each duplicate by actual block type, deletes or repairs invalid references, clones duplicate data blocks when possible, and updates bitmaps to reflect the remaining owner.

## Main Elements
- Data structures:
  - `fxn_info`: search state for a block.
  - `dup_handler`: live duplicate tree/ref counts while repairs mutate the tree.
  - `clone_target`: target block and first-reference flag for cloning.
  - `meta_blk_ref`: metadata block/offset where a target data reference was found.
- Reference discovery:
  - `find_block_ref()` loads a dinode, records self-reference, walks metadata/data/EA references, and adds refs for known duplicates.
  - `check_leaf_refs()`, `check_metalist_refs()`, `check_data_refs()`, `check_eattr_*_refs()` are metawalk callbacks that call `add_duplicate_ref()`.
- Duplicate logging and accounting:
  - `log_inode_reference()` reports per-inode duplicate reference type counts.
  - `revise_dup_handler()` recalculates reference counts after each mutation.
- Repair actions:
  - `resolve_dup_references()` removes invalid references first, then wrong-type references, then extra valid references. It can remove EAs, delete corrupt dinodes, run delete callbacks over metadata trees, remove tree/link state, and delete duplicate list entries.
  - `clone_data_block()` finds a specific data pointer and clones it.
  - `clone_data()` allocates a replacement block, copies content, rewrites the pointer, or optionally zeroes the reference.
  - `clone_dup_ref_in_inode()` clones repeated references to the same duplicate within one inode.
  - `resolve_last_reference()` sets the final block bitmap state from the surviving reference type and deletes the duplicate tree node.
  - `handle_dup_blk()` drives the full four-step duplicate resolution for one block.
- `pass1b()`: scans all dinode blocks to discover original duplicate references, then drains `cx->dup_blocks` by calling `handle_dup_blk()`.

## Control Flow
If the duplicate tree is empty, pass1b exits. Otherwise it scans block numbers up to `last_fs_block`, uses bitmap states to find dinodes, and calls `find_block_ref()` until all original duplicate references are found or the scan ends. It then repeatedly takes the first duplicate tree node, logs references, determines the acceptable reference type from the duplicate block’s on-disk metadata header, removes invalid references, removes wrong-type references, removes extra valid references, and fixes or frees the remaining block state.

## Dependencies And Integration
Uses duplicate-tree/list APIs from fsck common code, delete callbacks from `afterpass1_common.h`, metawalk traversal, link and inode/directory tree cleanup, bitmap repair from `metawalk.c`, and libgfs2 allocation/buffer/inode APIs.

## Risk Notes
Pass1b repairs can delete inodes, remove extended attributes, free metadata/data trees, clone blocks, and change bitmap state. It constantly recomputes duplicate counts because repairs mutate the duplicate tree. User “no” answers can leave references unresolved, in which case pass1b preserves remaining refs rather than silently forcing a repair.
