# sources/test-tools/fio/flist.h

Purpose: fio's Linux-kernel-style intrusive doubly linked list helper. It provides compact list-head manipulation used by many fio structures without separate list node allocations.

Important APIs/types/functions: defines `container_of`, `struct flist_head`, `FLIST_HEAD_INIT`, `FLIST_HEAD`, `INIT_FLIST_HEAD`, add/delete/splice helpers, `flist_empty`, entry accessors, iteration macros `flist_for_each` and `flist_for_each_safe`, and external `flist_sort`.

Control flow: callers embed `struct flist_head` in their own object, initialize a list head or node, add nodes at head/tail, remove or remove-and-reinitialize nodes, splice lists, and iterate with either ordinary or safe traversal depending on whether deletion can occur during iteration.

State and persistence behavior: list state is purely pointer links in caller-owned memory. Deleting with `flist_del` poisons the entry's next/prev to `NULL`; `flist_del_init` makes it an empty singleton. There is no synchronization or persistence; locking is the caller's responsibility.

Dependencies/integration: depends only on stdlib/stddef. It is used by file lists, flow lists, GUI option lists, debug timing hash buckets, and many other fio modules.

Risks and test signals: intrusive lists fail hard when entries are not initialized, are double-deleted, or are removed during unsafe iteration. `container_of` relies on compiler `__typeof__`. Test signals should cover add/tail ordering, safe deletion while iterating, splice-and-init semantics, empty-list behavior, and sanitizer runs for double delete or uninitialized nodes.
