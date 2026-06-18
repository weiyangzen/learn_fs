## sources/security-integrity/audit-userspace/src/ausearch-nvpair.c

Purpose: small name/value linked-list cache, primarily for uid-to-name lookup.

Important APIs/functions: `search_list_create()`, `search_list_append()`, `search_list_find_val()`, and `search_list_clear()`.

Control flow: lookup code initializes a list, appends heap-owned names paired with numeric values, scans linearly for cached values, and clears names/nodes at shutdown.

State/persistence: caller-owned list only; no static state in this module. `search_list_append()` shallow-transfers `node->name` into a heap node.

Dependencies/integration: used by `ausearch-lookup.c` and `ausearch-parse.c` UID lookup caches.

Risks/test signals: append walks from `cur` to the end, so a stale `cur` must still be valid. No duplicate prevention is built in. Tests should cover cache hit/miss, clear after empty and populated lists, and ownership of appended names.
