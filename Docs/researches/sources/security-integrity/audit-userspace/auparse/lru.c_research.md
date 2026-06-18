<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/lru.c -->
# sources/security-integrity/audit-userspace/auparse/lru.c

## Purpose
Implements a small dual-key least-recently-used cache used by auparse UID/GID name resolution.

## Important APIs, types, and functions
Exported hidden functions are `init_lru`, `destroy_lru`, `check_lru_uid`, and `check_lru_name`. Internals allocate `Queue`, `Hash`, and `QNode` objects, maintain a doubly linked recency list, hash names using djb2, evict tail nodes, and update parallel UID/name hash slots.

## Control flow
`check_lru_uid` or `check_lru_name` indexes the relevant hash array. A matching node is moved to the front and counted as a hit. A miss frees a colliding node or evicts the list tail when full, allocates a new node, inserts it at the front, and stores it in the hash. Destruction repeatedly dequeues all nodes before freeing hash arrays.

## State and persistence behavior
`Queue` tracks count, total size, hit/miss/eviction counters, front/end list pointers, hash arrays, a debug name, and an unused cleanup callback. State is in-memory and parser-owned.

## Dependencies and integration points
Depends on libc allocation/string functions, `lru.h`, and optional syslog debug logging. `interpret.c` uses it for per-parser UID and GID caches.

## Risks and test signals
Risks include direct-mapped hash collision eviction reducing cache quality, `qsize == 0` division, stale parallel hash links if node identity changes, and currently unused cleanup callbacks. Tests should cover hit promotion, collision replacement, capacity eviction, destroy after mixed uid/name entries, and cache metrics.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/lru.c -->
