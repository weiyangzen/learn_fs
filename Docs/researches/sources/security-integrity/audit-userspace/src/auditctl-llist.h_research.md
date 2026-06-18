# sources/security-integrity/audit-userspace/src/auditctl-llist.h

Purpose: type and function declarations for auditctl's local rule linked list.

Important APIs/types: defines `lnode` with `struct audit_rule_data *r`, `size`, and `next`; defines `llist` with `head`, `cur`, and `cnt`; declares list manipulation functions and inline `list_get_cur`.

Control flow: none in header except the trivial current-node accessor.

State and persistence: caller-owned in-memory list state only.

Dependencies and integration: includes `config.h`, `sys/types.h`, and `libaudit.h`; used by `auditctl-listing.c`.

Risks and test signals: no ownership annotations beyond comments; misuse can leak or double-free copied rule data. Build plus listing tests cover normal usage.
