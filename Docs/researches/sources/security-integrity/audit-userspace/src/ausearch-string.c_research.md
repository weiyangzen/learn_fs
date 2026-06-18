## sources/security-integrity/audit-userspace/src/ausearch-string.c

Purpose: linked-list container for strings with hit counts, used by report aggregators and parsed field lists.

Important APIs/functions: `slist_create()`, `slist_append()`, `slist_next()`, `slist_clear()`, `slist_add_if_uniq()`, and `slist_sort_by_hits()`. Sorting uses a small-list bubble-style algorithm and merge sort for lists of 200 or more.

Control flow: callers append preallocated `snode` strings or call `slist_add_if_uniq()` to deduplicate and count hits. `slist_sort_by_hits()` reorders nodes descending by hit count and resets `cur`.

State/persistence: caller-owned list; no module-static state. `slist_clear()` frees both `str` and `key` in every node.

Dependencies/integration: used by `search_items` filename/key lists, node filters, and `summary_data` report lists.

Risks/test signals: `slist_append()` shallow-transfers `str` and `key`; callers must allocate or otherwise ensure freeable ownership. Merge sort does not update `last`, which can break subsequent appends after sorting. Tests should cover append after sort, duplicate hit increments, key ownership, clear, and large summary lists.
