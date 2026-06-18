## sources/security-integrity/audit-userspace/src/ausearch-int.h

Purpose: declares the small integer linked-list abstraction used by filters and report aggregators.

Important APIs/types: `int_node` stores `num`, `hits`, `aux1`, and `next`; `ilist` stores head/current/count. Inline helpers reset to first and get current node. Public functions create, append, clear, add unique, iterate, and sort by hits.

Control flow/state: consumers commonly call `ilist_first()`, inspect `ilist_get_cur()`, then advance with `ilist_next()`. Cursor state is mutable and belongs to the list.

Dependencies/integration: included by `ausearch-options.h` and `aureport-scan.h`, exposing it across command parsing and reporting.

Risks/test signals: no ownership beyond nodes. Cursor-based iteration is not thread-safe or reentrant. Tests should include multiple independent traversals that reset the cursor before reuse.
