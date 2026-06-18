# sources/user-network-fs/samba/source3/libsmb/libsmb_misc.c

Purpose: provides one small shared utility for validating whether an `SMBCFILE *` belongs to a context-owned doubly linked list.

Important API: `SMBC_dlist_contains(SMBCFILE *list, SMBCFILE *p)` returns false for null list or target and otherwise walks `next` pointers until it finds pointer identity equality.

Control flow/state: there is no allocation, persistence, or mutation. The function is intentionally pointer-based: it does not compare file names, descriptors, or server fields. It is used as a guard in file, directory, stat, and compatibility operations before dereferencing handles supplied by callers.

Dependencies and integration: depends on `libsmbclient.h` / `libsmb_internal.h` for `SMBCFILE`. It integrates with all APIs that maintain `context->internal->files`, including open, close, read/write, directory reads, and fstat.

Risks: this only validates membership in the current in-memory list; it does not protect against concurrent mutation by another thread unless higher-level synchronization is active. A stale pointer that has been freed and reallocated into the list could theoretically pass pointer identity checks. Test signals: null list, null element, first/middle/last match, non-member pointer, and calls after close returning `EBADF` through higher-level APIs.
