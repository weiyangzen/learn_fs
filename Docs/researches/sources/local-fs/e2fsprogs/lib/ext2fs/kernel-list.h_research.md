# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/kernel-list.h

Small Linux-style doubly linked list implementation. It defines `struct list_head`, initialization macros, insertion at head/tail, deletion, emptiness check, splice, and `list_entry()` via `container_of`.

The implementation is minimal and assumes callers maintain object lifetime and avoid double deletion. It is used as compatibility infrastructure by kernel-derived userspace code.
