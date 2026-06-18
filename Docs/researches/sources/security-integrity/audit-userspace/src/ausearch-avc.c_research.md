## sources/security-integrity/audit-userspace/src/ausearch-avc.c

Purpose: minimal linked-list implementation for AVC/SELinux context data attached to parsed audit events.

Important APIs/functions: `alist_create()`, `alist_append()`, `alist_next()`, `alist_clear()`, `anode_init()`, `anode_clear()`, and filtered search/iteration helpers `alist_find_subj()`, `alist_next_subj()`, `alist_find_obj()`, `alist_next_obj()`, `alist_find_avc()`, `alist_next_avc()`.

Control flow: parsers allocate strings into a stack `anode`, call `alist_append()`, and the list takes pointer ownership by shallow-copying fields into a heap node. Matching/reporting routines position `cur` on the first node with subject/object/AVC result and iterate matching nodes.

State/persistence: only caller-owned `alist` state; no static state or persistence. `alist_clear()` frees all node strings through `anode_clear()`.

Dependencies/integration: used by `ausearch-parse.c` for parsed subject/object/AVC info, `ausearch-match.c` for context filters, `aureport-scan.c` for AVC summaries, and `ausearch-lookup.c` for result interpretation.

Risks/test signals: appends transfer raw pointers, so callers must not also free successful fields. Failed append paths can leak caller-allocated fields unless caller clears the temporary node. Cursor state is mutable and reused by find/next APIs. Tests should cover multiple AVC records per event, mixed subject/object-only nodes, clear after partial construction, and OOM behavior.
