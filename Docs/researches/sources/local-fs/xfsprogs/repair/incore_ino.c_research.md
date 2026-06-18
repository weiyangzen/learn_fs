# File Research: sources/local-fs/xfsprogs/repair/incore_ino.c

## Role

`incore_ino.c` implements repair’s in-memory inode trees and uncertain-inode trees.

## Inode Tree Model

Each `ino_tree_node_t` represents one 64-inode chunk. The main inode tree stores confirmed inode chunks. The uncertain tree stores candidate chunks discovered from directory references before repair has confirmed whether they exist.

## Link Count Storage

The file uses dynamically growing arrays for disk and counted nlinks:

- Start with `uint8_t`.
- Grow to `uint16_t` when values exceed 255.
- Grow to `uint32_t` when values exceed 65535.

This saves memory for large filesystems where most nlink counts are small.

Functions:

- `add_inode_ref`
- `drop_inode_ref`
- `num_inode_references`
- `set_inode_disk_nlinks`
- `get_inode_disk_nlinks`

## Inode Record Allocation

`alloc_ino_node` initializes a chunk as all free and unconfirmed, allocates disk nlink storage, optional filetype storage, clears metadata/reflink/dir masks, and initializes a mutex.

`free_ino_tree_node` releases nlink arrays, extended data, parent arrays, filetypes, mutex, and the record.

## Uncertain Inodes

`add_aginode_uncertain` rounds the inode down to a 64-inode chunk, uses a per-AG last-record cache, creates a record if needed, and marks the candidate free or used.

`add_inode_uncertain` converts fs inode number to AG/in-AG form.

`get_uncertain_inode_rec`, `findfirst_uncertain_inode_rec`, `find_uncertain_inode_rec`, and `clear_uncertain_ino_cache` support phase 3 processing of newly discovered candidate inodes.

## Confirmed Inode Trees

`add_inode` creates and inserts a confirmed inode record.

`set_inode_used_alloc` and `set_inode_free_alloc` add a new chunk and mark a specific inode used or free.

`get_inode_rec` removes a record from the main inode tree.

`find_inode_rec_range` finds inode records overlapping a range.

`print_inode_list` and `print_uncertain_inode_list` are debugging utilities.

## Parent Tracking

`set_inode_parent` stores parent inode numbers in a packed `parent_list_t` indexed by bit position. It supports both the early-phase parent-list union field and the later extended-data parent list.

`get_inode_parent` returns a stored parent or zero.

## Extended Phase Data

`alloc_ex_data` converts a record from early parent-only data to full extended data:

- Preserves existing parent list.
- Allocates counted nlink storage matching current nlink width.
- Initializes reached/processed masks to zero.

`add_ino_ex_data` applies this to every confirmed inode record and sets `full_ino_ex_data`.

## Initialization

`incore_ino_init` allocates per-AG main and uncertain AVL trees, initializes them with inode-range operations, allocates the uncertain last-record cache, and starts with compact inode data mode.

## Interactions

- Phase 2 creates or marks root and metadata inode chunks.
- Phase 3 adds uncertain inodes from directory entries and confirms them after validation.
- Phase 6/7 use extended data for reachability, parent, and nlink validation.
