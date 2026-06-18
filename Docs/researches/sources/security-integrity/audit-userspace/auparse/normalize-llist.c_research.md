<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/normalize-llist.c -->
# sources/security-integrity/audit-userspace/auparse/normalize-llist.c

## Purpose
Implements a minimal singly linked list used by normalization to store subject and object attribute field coordinates.

## Important APIs, types, and functions
Functions are `cllist_create`, `cllist_clear`, `cllist_next`, and `cllist_append`. Nodes store a numeric coordinate and optional data pointer.

## Control flow
Create initializes empty head/current/tail pointers. Append allocates a node, links it at tail, makes it current, and increments count. Iteration starts with inline `cllist_first` from the header, then `cllist_next`. Clear walks nodes, optionally calls the list cleanup callback on node data, frees nodes, and resets the list.

## State and persistence behavior
State is in-memory list ownership inside `normalize_data.actor.attr` and `normalize_data.thing.attr`.

## Dependencies and integration points
Depends on `normalize-llist.h` and libc allocation. `normalize.c` appends encoded record/field locations for later getter iteration.

## Risks and test signals
Risks are allocation failure propagation, callback misuse, and stale current pointers after clear. Tests should cover append order, iteration, cleanup callback invocation, and clear on null/empty lists.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/normalize-llist.c -->
