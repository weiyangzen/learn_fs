# File Research: sources/os/bsd/netbsd-src/lib/libc/include/isc/list.h

Macro-based intrusive doubly-linked list utilities from ISC.

Defines:
- `LIST(type)` and `LINK(type)` struct fragments.
- Initialization, linked-state, head/tail/empty accessors.
- Operations: `PREPEND`, `APPEND`, `UNLINK`, `INSERT_BEFORE`, `INSERT_AFTER`, `ENQUEUE`, `DEQUEUE`.

Uses `INSIST` assertions to catch misuse such as inserting already-linked elements or unlinking unlinked elements.
