# File Research: sources/local-fs/reiserfsprogs/reiserfscore/prints.c

## Purpose
`prints.c` implements diagnostic and debug printing for ReiserFS metadata, including custom printf specifiers, item/node dumps, superblock dumps, bitmap dumps, object-id maps, and journal transaction summaries.

## Main Responsibilities
- Registers ReiserFS-specific printf specifiers through glibc printf hooks.
- Prints keys, short keys, item headers, block headers, disk children, modes, and UUIDs.
- Dumps directory items, indirect items, stat-data items, direct item bodies, leaves, internals, and generic blocks.
- Prints superblock and journal parameter details.
- Prints tree-balance state.
- Prints bitmap usage ranges and object-id maps.
- Prints journal headers and transactions.

## Key Functions
- `reiserfs_warning()` lazily registers specifiers `%K`, `%k`, `%H`, `%b`, `%y`, `%M`, and `%U`, then delegates to `vfprintf`.
- `print_directory_item()` prints directory entry names, key targets, hash/generation, location, state, and detected hash function.
- `print_indirect_item()` coalesces consecutive indirect block pointers into compact sequences.
- `print_stat_data()` decodes old and new stat-data layouts and returns whether the item represents a symlink.
- `reiserfs_print_item()` prints one item for debug tooling.
- `print_internal()` and `print_leaf()` dump formatted tree nodes.
- `print_super_block()` prints filesystem format, block counts, clean state, tree height, hash function, object-id map size, journal parameters, fs state, UUID/label, mount-count fields, and check interval.
- `print_block()` dispatches descriptor, superblock, leaf, internal, or unformatted output.
- `print_tb()` dumps `struct tree_balance` buffers and balance parameters.
- `print_bmap()` and `print_bmap_block()` print bitmap block ranges and used/free counts.
- `print_objectid_map()` prints busy/free object-id intervals.
- `print_journal_header()`, `print_one_transaction()`, and `print_journal()` print journal metadata and transaction block mappings.

## Data and Control Flow
Printing generally performs lightweight format recognition before decoding. `print_block()` tries journal descriptor, superblock, leaf, internal, then unknown data. Leaf printing can run in summary mode or detailed mode. In detailed mode it prints every real item and dispatches by item type.

The custom specifier system centralizes formatting for keys and on-disk structures. Most output goes through `reiserfs_warning()`, even for normal diagnostic output, to gain those specifiers.

## Integration Points
- Depends on format helpers from `node_formats.c`.
- Uses journal iteration from `journal.c`.
- Uses misc/device helpers and UUID support when available.
- Used by debug tools and error paths throughout reiserfsprogs.

## Risks and Edge Cases
- Global `is_symlink` state in leaf printing can affect direct-item rendering across items.
- `timestamp()` uses a single static buffer and `localtime()`, so it is not thread-safe.
- Custom printf registration is process-global.
- `reiserfs_print_item()` appears to compute the item index using pointer subtraction divided by `sizeof(struct item_head)`, even though pointer subtraction already returns element count.
- Detailed direct-item printing may emit arbitrary file bytes to the output stream.
- Some `asprintf()` results are checked only through `len == -1`; allocation failure paths are minimal.

## Testing Signals
Tests should cover custom format specifiers, old/new stat-data, directory entries with bad locations, indirect sequence compaction, superblock short/full printing, bitmap spread and packed layouts, object-id maps, journal printing, and `print_block()` dispatch for all recognized block classes.
