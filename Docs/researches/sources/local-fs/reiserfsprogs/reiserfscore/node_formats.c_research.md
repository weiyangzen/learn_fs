# File Research: sources/local-fs/reiserfsprogs/reiserfscore/node_formats.c

## Purpose
`node_formats.c` defines core ReiserFS on-disk format recognition, validation, key/type conversion, hash mapping, directory item validation, stat-data access, object-id map manipulation, and block classification helpers.

## Main Responsibilities
- Recognizes leaves, internal nodes, superblocks, journal descriptors, and unknown blocks.
- Validates leaf header/item-header consistency.
- Validates internal node fixed-size layout.
- Handles ReiserFS 3.5, 3.6, and non-standard-journal magic strings.
- Calculates required journal start locations.
- Classifies bitmap, journal, data, and journalable blocks.
- Maps hash codes/names/functions.
- Validates directory entries and indirect items.
- Builds empty directory stat-data and directory item bodies.
- Converts between key formats, offsets, types, and uniqueness values.
- Gets/sets v1/v2 stat-data fields.
- Tracks used object IDs in the superblock object-id map.

## Key Functions
- `leaf_count_ih()`, `leaf_free_space_estimate()`, `is_a_leaf()`, and `leaf_item_number_estimate()` inspect leaf item-header arrays.
- `is_correct_internal()` and `is_tree_node()` validate formatted tree nodes.
- `who_is_this()` classifies a raw block buffer.
- `block_of_journal()`, `block_of_bitmap()`, `not_data_block()`, and `not_journalable()` classify block-number roles.
- `get_journal_start_must()` chooses old/new journal placement based on superblock location.
- `get_bytes_number()` returns logical byte coverage for direct/indirect items.
- `is_properly_hashed()`, `find_hash_in_use()`, `code2name()`, `func2code()`, `code2func()`, and `name2func()` bridge directory hash functions and stored hash codes.
- `is_it_bad_item()` validates stat-data, direct, directory, and indirect item bodies.
- `make_dir_stat_data()`, `make_empty_dir_item_v1()`, and `make_empty_dir_item()` synthesize directory metadata.
- `key_format()`, `get_offset()`, `get_type()`, `set_type()`, `set_offset()`, and `set_type_and_offset()` abstract v1/v2 key layouts.
- `entry_length()`, `name_in_entry()`, and `name_in_entry_length()` decode directory entries.
- `get_set_sd_field()` reads or writes common stat-data fields across old/new formats.
- `is_objectid_used()` and `mark_objectid_used()` query/update the object-id interval map.
- `is_blocksize_correct()` checks supported power-of-two block sizes from 512 to 8192.

## Data and Control Flow
Block classification is layered: superblock magic first, then leaf recognition, internal recognition, journal descriptor magic, then unknown. Leaf recognition distinguishes a fully consistent leaf from a damaged block that still has a plausible item-header array.

Hash detection starts with filesystem hash unset; directory validation tries known hashes against a name and offset, setting `reiserfs_hash(fs)` if exactly one function matches. Ambiguous matches leave the hash unknown but do not necessarily fail the entry.

Object-id map logic treats the superblock tail as alternating busy/free boundaries. `mark_objectid_used()` expands, shrinks, merges, or appends intervals depending on the target object ID and available map space.

## Integration Points
- Used by journal replay for descriptor detection and target block safety.
- Used by balancing code for key offsets, item type, directory entry sizing, and byte coverage.
- Used by print/debug code to decode nodes, superblocks, directories, bitmaps, and object IDs.
- Used by mkfs/fsck-style code to synthesize stat-data and empty directories.

## Risks and Edge Cases
- Directory validation can optionally treat hash mismatch as fatal via `bad_dir`.
- `is_bad_indirect()` delegates block-pointer validation through a callback, so safety depends on caller-provided policy.
- Object-id map updates modify packed superblock data in place and must maintain interval ordering.
- Leaf recognition intentionally tolerates damaged block headers when item-header arrays look plausible, which is useful for repair but risky if callers assume full validity.
- Hash names include quoted strings such as `"tea"`, so callers of `name2func()` must pass matching quoted names.

## Testing Signals
Tests should cover valid/corrupt leaves, internal nodes, journal descriptors, all superblock magic variants, old/new journal starts, bitmap layouts, directory hash detection ambiguity, bad directory locations, indirect item pointer validation, v1/v2 key conversion, stat-data field access, and object-id interval map transitions.
