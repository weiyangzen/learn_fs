# File Research: sources/local-fs/ntfs-3g/ntfsprogs/list.h

Provides a small Linux-kernel-style intrusive doubly linked list implementation for ntfsprogs. It defines `struct ntfs_list_head`, static/list-head initializers, add-at-head, add-at-tail, delete, delete-and-reinitialize, empty check, splice, container lookup, and simple/safe iteration macros.

The implementation is header-only using `static __inline__` helpers and macros. `ntfs_list_del()` leaves the removed node in an undefined linkage state, while `ntfs_list_del_init()` reinitializes it as a singleton list. `ntfs_list_splice()` prepends one non-empty list after a target head without reinitializing the source head.

Dependencies are minimal: it is generic C list manipulation and expects callers to embed `struct ntfs_list_head` in their own structures. Invariants are the usual intrusive-list rules: nodes must be initialized before use, cannot be inserted into multiple lists simultaneously, and safe iteration must be used when deleting during traversal.
