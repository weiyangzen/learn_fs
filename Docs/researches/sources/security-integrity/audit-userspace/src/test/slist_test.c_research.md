<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/test/slist_test.c -->
# sources/security-integrity/audit-userspace/src/test/slist_test.c

**Purpose**
This test validates the string list helper used by audit search code, covering unique insertion, append, clear, and sorting by duplicate hit counts.

**Important APIs, Types, And Functions**
It exercises `slist_create`, `slist_add_if_uniq`, `slist_first`, `slist_get_cur`, `slist_next`, `slist_append`, `slist_clear`, and `slist_sort_by_hits` over `slist`, `snode`, and the global list `s`. `print_list` iterates the list and returns the visible node count.

**Control Flow**
The test inserts three unique strings, checks count and iteration count, appends an explicit fourth node, attempts to add a duplicate `test2`, clears the list, then inserts a deliberate hit-count distribution. After sorting, it expects hit counts to descend from 4 to 1.

**State And Persistence**
State is entirely in process memory. The test allocates `n.str` with `strdup` before appending and relies on `slist_clear` to free list-owned string data.

**Dependencies And Integration Points**
It includes `ausearch-string.h` and links `ausearch-string.o` as configured in `src/test/Makefile.am`.

**Risks**
Like the integer-list test, it checks counts more strongly than string ordering after sort. Manual construction of an `snode` tests ownership transfer but could mask API assumptions if append semantics change.

**Test Signals**
Success means the list count, duplicate-hit increment, clear behavior, and descending hit-count sort all satisfy expected behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/test/slist_test.c -->
