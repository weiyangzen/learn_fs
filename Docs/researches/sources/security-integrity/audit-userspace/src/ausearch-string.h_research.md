## sources/security-integrity/audit-userspace/src/ausearch-string.h

Purpose: declares the string list abstraction used for filters, parsed fields, and report summaries.

Important APIs/types: `snode` stores `str`, optional `key`, hit count, and next pointer; `slist` stores head/current/last/count. Public APIs create, iterate, append, clear, add unique, and sort by hits.

Control flow/state: cursor-based iteration starts with `slist_first()` and advances with `slist_next()`. `last` accelerates append.

Dependencies/integration: included by common/search/list/report headers, making it a core utility type.

Risks/test signals: ownership is implicit but `slist_clear()` frees node strings. Tests should include lists where `key` is populated by path parsing and appends after sorting.
