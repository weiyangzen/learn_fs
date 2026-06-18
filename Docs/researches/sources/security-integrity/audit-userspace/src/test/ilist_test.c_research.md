<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/test/ilist_test.c -->
# sources/security-integrity/audit-userspace/src/test/ilist_test.c

**Purpose**
This standalone test validates the integer list helper used by ausearch-style code, especially unique insertion order and hit-count sorting.

**Important APIs, Types, And Functions**
The file exercises `ilist_create`, `ilist_add_if_uniq`, `ilist_first`, `ilist_get_cur`, `ilist_next`, `ilist_sort_by_hits`, and `ilist_clear` over `ilist` and `int_node`.

**Control Flow**
The first phase inserts numbers in mixed order and iterates from the first node, expecting `node->num` to increase from 0 through 9. The second phase clears the list, inserts duplicate values with different frequencies, sorts by `hits`, and expects hit counts to descend from 4.

**State And Persistence**
All state is in the in-memory linked list. `ilist_clear` is used between phases and before exit.

**Dependencies And Integration Points**
It includes `ausearch-int.h` and links `${top_builddir}/src/ausearch-int.o` from the Makefile. It is registered as an Automake check program.

**Risks**
The sort test validates hit counts but not the exact associated integer values after sorting, so a bug that preserves count sequence while mixing identities might pass. It also exits immediately on failure and may leak the list on early return.

**Test Signals**
A passing run indicates sorted unique insertion and hit-count sorting retain the expected basic invariants for integer search lists.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/test/ilist_test.c -->
