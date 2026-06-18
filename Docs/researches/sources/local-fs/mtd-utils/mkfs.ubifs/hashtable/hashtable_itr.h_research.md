# File Research: sources/local-fs/mtd-utils/mkfs.ubifs/hashtable/hashtable_itr.h

## Purpose
Declares and partially defines the hashtable iterator API.

## Main Definitions
- Concrete `struct hashtable_itr` stores the table, current entry, parent entry, and bucket index.
- `hashtable_iterator_key()` and `hashtable_iterator_value()` inline access to the current entry.
- Declares iterator construction, advance, remove, and search functions.
- `DEFINE_HASHTABLE_ITERATOR_SEARCH` generates typed search wrappers.

## Dependencies
Includes `hashtable.h` and `hashtable_private.h` so accessors can inline against `struct entry`.

## Risks and Notes
Because the iterator structure is public in this header, callers can depend on internals that are otherwise private to the hashtable implementation.
