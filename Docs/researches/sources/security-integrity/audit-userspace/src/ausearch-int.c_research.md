## sources/security-integrity/audit-userspace/src/ausearch-int.c

Purpose: linked-list container for integer values with hit counts, used for message-type filters and report summaries.

Important APIs/functions: `ilist_create()`, `ilist_append()`, `ilist_next()`, `ilist_clear()`, `ilist_add_if_uniq()`, and `ilist_sort_by_hits()`. `swap_nodes()` supports hit sorting.

Control flow: callers append explicit values or use `ilist_add_if_uniq()` to maintain ascending numeric order while incrementing `hits` for duplicates. Summary output can sort by descending hit count.

State/persistence: caller-owned heap list; no static state. `ilist_clear()` tolerates null list pointers.

Dependencies/integration: used by `ausearch-options.c` for `event_type`, by `aureport-scan.c` for summary counters, and by output code that prints top values.

Risks/test signals: `ilist_append()` assumes `cur` is the tail when appending to a non-empty list. `ilist_add_if_uniq()` changes list order and cursor state. The hit sort is quadratic restart-on-swap. Tests should cover head/middle/tail insertion, duplicate hit increments, sort stability expectations, and clearing empty/null lists.
