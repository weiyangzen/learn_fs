# sources/sync-backup/casync/src/canametable.h

## Purpose
`canametable.h` declares the name-table data structures used to carry directory-entry archive context in `CaLocation` metadata. It defines a compact list of filename hashes and serialized archive offset ranges, optionally chained to a parent table.

## Important APIs, Types, and Functions
`CaNameItem` stores `hash`, `start_offset`, and `end_offset`. `CaNameTable` stores a reference count, parent pointer, `entry_offset`, item counts, a cached `formatted` string, and flexible-array `items[]`. Public functions allocate, reference, unreference, append, format, parse, convert to BST layout, dump, recursively dump, and compare tables. Inline accessors expose item counts, indexed lookup, and the last item.

## Control Flow
Callers normally allocate a table, append items as directory entries are serialized, attach parent context, then format it into a location string. Readers parse the string back into an equivalent table chain and may use the BST conversion for faster lookup.

## State and Persistence
State is heap-based and reference counted. `formatted` is a cached serialized representation owned by the table. Persistence is textual and embedded in higher-level metadata, not directly file-backed.

## Dependencies and Integration Points
The header depends on `util.h` and `realloc-buffer.h`. It is included by `calocation.h`, so it participates in location formatting, hardlink identity, and archive traversal metadata.

## Risks
Internals are public, so callers can mutate without invalidating `formatted` or respecting copy-on-write. Offset fields are unsigned 64-bit values; callers must avoid nonsensical ranges such as `end_offset < start_offset`.

## Test Signals
Indirectly tested by `test/test-calocation.c`. Header-level contract should be protected by tests for append/accessor behavior and parent-chain equality.
