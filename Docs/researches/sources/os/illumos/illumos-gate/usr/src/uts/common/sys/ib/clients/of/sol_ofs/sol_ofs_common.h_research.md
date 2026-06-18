# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_ofs/sol_ofs_common.h

This common Solaris OFS utility header provides user-object tables, small linked-list abstractions, generic resource lists, and debug printf entry points shared by OpenFabrics kernel drivers.

Core definitions:
- User object types cover sol_uverbs contexts, PDs, AHs, MRs, CQs, SRQs, QPs, event files, and sol_ucma event files, CM IDs, and multicast objects.
- `sol_ofs_uobj_t` carries a user handle, object type, rwlock, table ID, ref lock/refcount, live flag, and object size.
- `sol_ofs_uobj_table_t` is a growable block table mapping integer IDs to user objects.
- Table/object APIs initialize/finalize tables, initialize/ref/deref/put/free objects, add/remove objects, and acquire objects for read or write.
- `llist_head_t` is a Linux-style circular doubly linked list with explicit payload pointer.
- `genlist_t` is a separate doubly linked list of generic entries with helpers to add/delete/remove/insert/flush/test empty.
- Debug routines expose levels L0-L5.

Risk-sensitive invariants:
- Object lifetime combines rwlocks with explicit refcounts; callers must pair object gets/puts correctly.
- `llist_head_t` and `genlist_t` do not self-synchronize; external locking is required.
- Object table block sizing and IDs are shared by uverbs and ucma, so type correctness matters at lookup boundaries.
