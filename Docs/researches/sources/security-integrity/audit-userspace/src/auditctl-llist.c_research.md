# sources/security-integrity/audit-userspace/src/auditctl-llist.c

Purpose: minimal singly linked list used by auditctl listing code to store copies of kernel rule data before printing.

Important APIs/functions: `list_create`, `list_first`, `list_last`, `list_next`, `list_append`, and `list_clear`.

Control flow: append allocates a node, optionally deep-copies a rule payload of caller-provided size, links at current tail, and makes the new node current. Clear walks all nodes, freeing copied rule data and nodes.

State and persistence: state is held in caller-owned `llist` structures; no globals or disk persistence.

Dependencies and integration: depends on `auditctl-llist.h` and `struct audit_rule_data`. Used by `auditctl-listing.c` for `AUDIT_LIST_RULES` buffering.

Risks and test signals: append assumes `l->cur` is the tail when list is nonempty; callers must use append consistently. Allocation failure returns 1. Test through `auditctl -l` with many rules and memory-checking builds.
