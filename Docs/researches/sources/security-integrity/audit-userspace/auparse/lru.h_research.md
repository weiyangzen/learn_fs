<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/lru.h -->
# sources/security-integrity/audit-userspace/auparse/lru.h

## Purpose
Declares auparse's internal LRU cache data structures and lookup lifecycle functions.

## Important APIs, types, and functions
Defines `QNode` with recency links, use count, uid, and name; `Hash` with an array of node pointers; and `Queue` with cache counters, recency endpoints, UID/name hash tables, label, and cleanup callback. Declares `init_lru`, `destroy_lru`, `check_lru_uid`, and `check_lru_name`.

## Control flow
Callers create a fixed-size queue, request nodes by UID or name, fill missing counterpart fields after NSS lookup, and destroy the queue during parser cleanup.

## State and persistence behavior
All cache state is in-memory and explicitly destroyed. No file persistence exists.

## Dependencies and integration points
Uses DSO visibility and `uid_t`. Consumed by `internal.h` and `interpret.c` for identity translation caches.

## Risks and test signals
Risks are external mutation of exposed structs and ownership assumptions for `name`. Tests should validate both lookup APIs and ensure parser teardown releases caches without leaks.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/lru.h -->
