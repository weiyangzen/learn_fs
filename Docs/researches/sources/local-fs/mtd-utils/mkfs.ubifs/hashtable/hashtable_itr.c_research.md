# File Research: sources/local-fs/mtd-utils/mkfs.ubifs/hashtable/hashtable_itr.c

## Purpose
Implements external iterators for the bundled hashtable.

## Main Entry Points
- `hashtable_iterator()` allocates an iterator positioned at the first entry, or an empty iterator if the table has no entries.
- `hashtable_iterator_advance()` moves within a bucket chain or to the next non-empty bucket.
- `hashtable_iterator_remove()` removes the current entry, frees its key, advances the iterator, and returns whether iteration can continue.
- `hashtable_iterator_search()` positions an existing iterator at a key match.

## Dependencies
Uses the public, private, and iterator hashtable headers. It relies on the concrete table and entry layout from `hashtable_private.h`.

## Risks and Notes
Iterator allocation is caller-owned, but some users in this tree do not free iterator objects after traversal, causing small leaks in utility execution. Removing through the iterator does not free the value, so callers must capture and release values themselves if needed.
