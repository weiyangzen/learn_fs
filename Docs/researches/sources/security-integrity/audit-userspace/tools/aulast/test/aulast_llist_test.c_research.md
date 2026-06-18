<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/aulast/test/aulast_llist_test.c -->
# sources/security-integrity/audit-userspace/tools/aulast/test/aulast_llist_test.c

**Purpose**
This unit test suite validates advanced behavior of the `aulast` session linked list, focusing on update correctness, deletion, find behavior, and session ID reuse.

**Important APIs, Types, And Functions**
The file uses `TEST_START`, `TEST_PASS`, and `TEST_FAIL` macros for simple reporting. `count_sessions` iterates without permanently changing `l->cur`. Test functions call `list_create`, `list_create_session`, `list_find_auid`, `list_update_start`, `list_update_logout`, `list_delete_cur`, `list_first`, `list_get_cur`, and `list_clear`.

**Control Flow**
`test_update_operations_verification` creates sessions, checks initial state, updates login fields, logs out, and verifies proof serials and NULL host/terminal handling. `test_repeated_add_remove_with_find` creates five sessions, deletes middle entries, reuses session IDs for different users, and removes all sessions while checking counts and absence. `test_complex_session_management` models multiple users, logout/delete, ID reuse, and batch logout checks. `main` runs all three and returns failure if any test did not pass.

**State And Persistence**
State is heap list data and local counters. Each test clears its list on success.

**Dependencies And Integration Points**
It includes the production `aulast-llist.h` and links the production `aulast-llist.c` via the test Makefile.

**Risks**
The tests intentionally continue after function calls without checking allocation failure paths. If a `TEST_FAIL` occurs before `list_clear`, temporary allocations can leak during that failed run.

**Test Signals**
The tests provide strong signals for cursor preservation, deletion semantics, update field mutation, and correct distinction between reused session IDs and old records.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/aulast/test/aulast_llist_test.c -->
