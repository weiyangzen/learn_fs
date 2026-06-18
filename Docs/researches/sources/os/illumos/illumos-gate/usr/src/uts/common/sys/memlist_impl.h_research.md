# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/memlist_impl.h

Purpose: Declares common internal helpers for allocating, freeing, inserting, deleting, finding, and modifying `struct memlist` spans.

Key APIs:
- Allocation/free: `memlist_get_one()`, `memlist_free_one()`, `memlist_free_list()`, `memlist_free_block()`.
- List mutation: `memlist_insert()`, `memlist_del()`.
- Lookup: `memlist_find()`.
- Span operations: `memlist_add_span()`, `memlist_delete_span()`.

Key return codes:
- `MEML_SPANOP_OK`
- `MEML_SPANOP_ESPAN`
- `MEML_SPANOP_EALLOC`

Relevance to subset A: Internal physical memory list manipulation.
