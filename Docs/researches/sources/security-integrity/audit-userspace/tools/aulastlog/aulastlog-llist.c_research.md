<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/aulastlog/aulastlog-llist.c -->
# sources/security-integrity/audit-userspace/tools/aulastlog/aulastlog-llist.c

**Purpose**
This file implements a small linked list of users and their latest successful login metadata for `aulastlog`.

**Important APIs, Types, And Functions**
It implements `list_create`, `list_next`, `list_append`, `list_clear`, `list_update_login`, `list_update_host`, `list_update_term`, and `list_find_uid`. `list_append` copies an input `lnode` into newly allocated storage, duplicates strings, assigns item order from `cnt`, and increments the count.

**Control Flow**
The CLI prepopulates the list from passwd entries. As audit login events are found, `list_find_uid` positions `cur`, then update functions mutate timestamp, host, and terminal for that user. Iteration for output uses `list_first`, `list_get_cur`, and `list_next`.

**State And Persistence**
State is process-local heap memory. The list owns duplicated `name`, `host`, and `term` strings and frees them in `list_clear`. There is no persistent state.

**Dependencies And Integration Points**
The implementation depends on libc allocation/string APIs and `aulastlog-llist.h`. `aulastlog.c` uses it as a fixed list of local users plus last-login data.

**Risks**
Allocation failures in `strdup` are not checked, so later reporting may see NULL fields unexpectedly. `list_update_host` and `list_update_term` set fields to NULL without freeing old values when passed NULL, which would leak if those paths are used after a value exists. The update helpers assume `l->cur` is valid.

**Test Signals**
No dedicated test in this subset covers this list; behavior is indirectly build-covered by `aulastlog` compilation.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/aulastlog/aulastlog-llist.c -->
