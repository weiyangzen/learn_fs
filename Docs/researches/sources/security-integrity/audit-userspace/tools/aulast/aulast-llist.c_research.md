<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/aulast/aulast-llist.c -->
# sources/security-integrity/audit-userspace/tools/aulast/aulast-llist.c

**Purpose**
This file implements the minimal linked list used by `aulast` to track currently open and completed login sessions while scanning audit events.

**Important APIs, Types, And Functions**
It implements `list_create`, `list_next`, internal `list_append`, `list_clear`, `list_create_session_simple`, `list_create_session`, `list_update_start`, `list_update_logout`, `list_delete_cur`, `list_find_auid`, and `list_find_session`. Nodes are `lnode` records defined in the header.

**Control Flow**
Creation initializes an empty head/current pair. Session creation allocates or accepts an `lnode`, initializes login metadata and proof serials, and appends it at the tail by walking from `cur` when necessary. Find functions scan linearly and set `l->cur` to the matching node. Update functions mutate the current node, duplicating host/terminal strings on login and setting end time/status on logout. Deletion walks from the head, removes the current node, frees owned strings and the node, then positions `cur` at the next node for head deletion or previous node otherwise.

**State And Persistence**
State is process-local heap memory. The list owns duplicated `name`, `term`, and `host` strings for normal allocated nodes. There is no durable persistence; `aulast` output is derived while scanning logs.

**Dependencies And Integration Points**
It depends on C allocation/string functions and the `aulast-llist.h` types. `aulast.c` uses it as its session cache.

**Risks**
`list_update_start` and `list_update_logout` check `l` but not `l->cur`, so callers must first position a current node. `list_create_session_simple` assumes the passed node is heap-owned and clearable, which is safe for `aulast.c` allocated nodes but dangerous for stack nodes.

**Test Signals**
`aulast_llist_test.c` exercises creation, update, deletion, repeated find/remove, and session ID reuse behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/aulast/aulast-llist.c -->
