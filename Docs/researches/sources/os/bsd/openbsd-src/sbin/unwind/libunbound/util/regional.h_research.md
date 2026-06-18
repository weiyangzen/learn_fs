# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/regional.h

Declares and documents the region allocator.

Key structure:
- `struct regional` stores chunk list head, large-object list head, large-byte total, first chunk size, available bytes, current data pointer, large-object threshold, and padding for alignment.

Public API:
- Creation: `regional_create`, `regional_create_custom`, `regional_create_nochunk`.
- Lifetime: `regional_free_all`, `regional_destroy`.
- Allocation: `regional_alloc`, `regional_alloc_init`, `regional_alloc_zero`, `regional_strdup`.
- Diagnostics: `regional_log_stats`, `regional_get_mem`.

Design notes:
- The first block is also the `struct regional`.
- Secondary chunks and large allocations form singly linked lists.
- This is intentionally simpler than NSD’s older region allocator: no recycle bin, cleanup list, function-pointer setup, or full stats collection.
