# sources/user-network-fs/samba/source3/include/adt_tree.h

## Purpose
`adt_tree.h` declares a small sorted path tree abstraction used by Samba utilities that need to add, search, and debug-print path-keyed data.

## Important APIs, Types, And Functions
- Opaque `struct sorted_tree`.
- `pathtree_init()` creates a tree with caller data and is freed via talloc.
- `pathtree_add()` adds a path component and associated data.
- `pathtree_find()` searches for a key.
- `pathtree_print_keys()` prints/debugs stored keys.

## Control Flow
Callers initialize a tree, add paths, perform lookups, and optionally print keys. Implementation details are hidden.

## State And Persistence
State is in the talloc-owned tree. There is no disk persistence.

## Dependencies And Integration Points
The header depends on Samba bool/talloc environment and is consumed by modules needing path-indexed in-memory lookup.

## Risks
Opaque semantics leave questions of normalization, case sensitivity, and ownership to the implementation. Callers must ensure key strings remain valid or are copied by the implementation.

## Test Signals
Test insertion/search with nested paths, duplicate paths, case variants, slash variants, and talloc cleanup.
