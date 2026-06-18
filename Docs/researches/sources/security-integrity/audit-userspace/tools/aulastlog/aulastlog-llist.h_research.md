<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/aulastlog/aulastlog-llist.h -->
# sources/security-integrity/audit-userspace/tools/aulastlog/aulastlog-llist.h

**Purpose**
This header declares the user last-login list used by `aulastlog`.

**Important APIs, Types, And Functions**
`lnode` stores last login seconds, uid, username, host, terminal, an item index, and next pointer. `llist` stores head/current pointers and a count. The API provides list creation, iteration, count access, append, clear, login/host/terminal updates, and lookup by uid.

**Control Flow**
`aulastlog.c` appends one node per passwd entry, scans audit records, uses uid lookup to position the current node, and updates the found node with newer login data.

**State And Persistence**
The represented state is in-memory summary data for one command invocation. It models a report table rather than a durable lastlog database.

**Dependencies And Integration Points**
It depends on `sys/types.h` for uid-related types and is included by the CLI and list implementation.

**Risks**
The structures are public and mutable, so callers can bypass count and ownership invariants. The API does not encode whether string pointers are borrowed or owned at input time; the implementation duplicates on append and update.

**Test Signals**
There is no direct unit test registered for this header in the listed files; build coverage comes from `aulastlog`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/aulastlog/aulastlog-llist.h -->
