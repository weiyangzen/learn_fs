<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/aulast/aulast-llist.h -->
# sources/security-integrity/audit-userspace/tools/aulast/aulast-llist.h

**Purpose**
This header declares the session list data model and operations used by the `aulast` audit-log session reporter.

**Important APIs, Types, And Functions**
`status_t` enumerates `LOG_IN`, `SESSION_START`, `LOG_OUT`, `DOWN`, `CRASH`, and `GONE`. `lnode` stores audit session id, start/end times, auid, pid, optional user/terminal/host strings, result, current status, audit proof serials, and next pointer. `llist` stores head and current pointers. The API includes creation, iteration, clearing, session creation/update/logout, current deletion, and lookup by `(auid,pid,session)` or session id.

**Control Flow**
`aulast.c` uses the header to keep a current-node cursor while scanning audit records. Inline helpers set or return the current pointer, while implementation functions maintain ownership and status transitions.

**State And Persistence**
The declared state is in-memory only. Proof serial fields preserve audit event references long enough for optional `--proof` output.

**Dependencies And Integration Points**
The header depends on `sys/types.h` for `uid_t` and `time_t` use via included platform headers. It is included by the tool and the list unit test.

**Risks**
The list exposes mutable structures directly, so callers can violate invariants such as ownership of string fields or valid status transitions. The `list_create_session_simple` API is especially sensitive because it appends an already allocated node.

**Test Signals**
The dedicated `aulast_llist_test` validates a subset of cursor, update, and delete behavior against this API.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/aulast/aulast-llist.h -->
