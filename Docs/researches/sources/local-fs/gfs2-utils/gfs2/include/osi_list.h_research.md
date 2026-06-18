# File Research: sources/local-fs/gfs2-utils/gfs2/include/osi_list.h

This header provides a minimal intrusive doubly linked list implementation.

It defines `struct osi_list`, `osi_list_t`, and macros for:
- Static declaration and initialization.
- Empty checks.
- Container lookup via `osi_list_entry`.
- Adding after or before a list head.
- Deleting, deleting with reinitialization.
- Forward iteration and safe forward iteration while deleting.

The API is modeled after kernel-style intrusive lists and is used by fsck duplicate-reference lists and other gfs2-utils structures.

Risks and notes:
- The macros do no membership validation.
- `osi_list_entry` uses pointer arithmetic on a null typed pointer, a common but low-level C container pattern.
- Safe iteration assumes the list is not concurrently modified outside the current loop.
