<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/normalize-llist.h -->
# sources/security-integrity/audit-userspace/auparse/normalize-llist.h

## Purpose
Declares the lightweight list type used by auparse normalization to hold variable-length attributes.

## Important APIs, types, and functions
Defines `data_node` with `num`, `data`, and `next`; `cllist` with head/current/tail, cleanup callback, and count. Inline helpers are `cllist_first` and `cllist_get_cur`; hidden functions cover create, clear, next, and append.

## Control flow
Normalization creates lists during parser initialization, appends record/field coordinates as attributes are discovered, then getter APIs iterate from first to next.

## State and persistence behavior
Per-normalization in-memory list state only.

## Dependencies and integration points
Included by `internal.h` for `normalize_data` and by `normalize.c` for attribute management.

## Risks and test signals
Risks are exposed mutable structs and callers forgetting to clear before reuse. Tests should validate normalization reset clears both subject and object attribute lists.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/normalize-llist.h -->
