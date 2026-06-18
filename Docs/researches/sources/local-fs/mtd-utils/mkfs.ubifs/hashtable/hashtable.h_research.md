# File Research: sources/local-fs/mtd-utils/mkfs.ubifs/hashtable/hashtable.h

## Purpose
Public header for the bundled generic hashtable library.

## Main API
Declares opaque `struct hashtable` plus `create_hashtable()`, `hashtable_insert()`, `hashtable_search()`, `hashtable_remove()`, `hashtable_count()`, and `hashtable_destroy()`.

## Convenience Macros
`DEFINE_HASHTABLE_INSERT`, `DEFINE_HASHTABLE_SEARCH`, and `DEFINE_HASHTABLE_REMOVE` generate typed wrappers around the void-pointer API for stronger compile-time checking in users that opt in.

## Dependencies
Implemented by `hashtable.c` and accompanied by iterator headers/source for traversal.

## Risks and Notes
The documented ownership model is important: inserted keys become owned by the table and are freed on removal/destruction, while values are only freed by `hashtable_destroy()` when requested.
