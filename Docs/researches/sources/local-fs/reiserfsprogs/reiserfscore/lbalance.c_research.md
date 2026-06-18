# File Research: sources/local-fs/reiserfsprogs/reiserfscore/lbalance.c

## Purpose
`lbalance.c` executes leaf-node item movement and mutation for ReiserFS balancing. It copies, shifts, merges, splits, inserts, pastes, cuts, and deletes leaf items according to `tree_balance` plans.

## Main Responsibilities
- Copies directory entries between leaf nodes.
- Merges boundary items when adjacent items are mergeable.
- Splits “liquid” direct, indirect, or directory items across nodes.
- Moves items from `S[0]` to left/right/new nodes or between neighbors.
- Inserts whole items into a leaf buffer.
- Pastes bytes or directory-entry space into an existing item.
- Cuts bytes or directory entries from an item.
- Deletes whole items from a leaf.
- Updates item headers, item locations, free-space counters, item counts, parent child sizes, and dirty flags.

## Key Functions
- `leaf_copy_dir_entries()` copies complete directory entries and creates or extends a destination directory item.
- `leaf_copy_boundary_item()` handles mergeable first/last items at node boundaries.
- `leaf_copy_items_entirely()` copies whole item headers and bodies.
- `leaf_item_bottle()` splits part of a direct, indirect, or directory item into another node.
- `leaf_copy_items()` combines boundary merging, whole-item copy, and partial-item copy.
- `leaf_move_items()` copies then deletes items from the source.
- `leaf_shift_left()` and `leaf_shift_right()` move items out of `S[0]` and update delimiting keys.
- `leaf_delete_items()` removes whole or partial items after movement.
- `leaf_insert_into_buf()` inserts a new item header and body into a leaf.
- `leaf_paste_in_buffer()` grows an existing item by bytes.
- `leaf_cut_entries()` and `leaf_cut_from_buffer()` remove directory entries or byte ranges.
- `leaf_paste_entries()` inserts directory entry headers and record bytes.
- `delete_item()` and `cut_entry()` are wrappers for single-buffer operations.

## Data and Control Flow
The file treats leaf node bodies as a compact region growing backward from block end while item headers grow forward after the block header. Insert/paste/cut/delete operations must move body bytes and then fix every affected `ih_location`.

Directory entries are special: the entry header array is at the start of the item body, while names/records are packed from the end backward. Copying and cutting directory entries therefore updates both `deh_location` values and item keys when the first entry changes.

## Integration Points
- Consumes `tree_balance` decisions from `fix_node.c`.
- Uses `replace_key()` to update parent delimiting keys after shifts.
- Uses `are_items_mergeable()` from `fix_node.c`.
- Uses item/key/directory helpers from `node_formats.c`.
- Called by higher-level balancing orchestration when leaf mutations are required.

## Risks and Edge Cases
- Directory entry manipulation is dense and location-sensitive; malformed `deh_location` values can cause overlapping `memmove`.
- Direct item split/merge updates offsets by bytes; indirect item split/merge updates offsets by `UNFM_P_SIZE * blocksize`.
- `leaf_paste_in_buffer()` prepares space for directory entries but leaves actual directory entry header insertion to `leaf_paste_entries()`.
- Boundary item merging can eliminate item headers, so parent child sizes and delimiter keys must stay synchronized.
- Several validation panics call `is_a_leaf()` after mutation, useful for catching corruption but abrupt in production tools.

## Testing Signals
Tests should cover full item copies, left/right boundary merges, directory item splits, direct item splits at head/tail, indirect item splits, insertion at beginning/middle/end, deleting all items, cutting directory entries including first entry key update, and parent child-size accounting.
