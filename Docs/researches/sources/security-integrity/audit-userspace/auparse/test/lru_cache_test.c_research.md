<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/lru_cache_test.c -->
# sources/security-integrity/audit-userspace/auparse/test/lru_cache_test.c

Purpose: small white-box test for auparse LRU cache internals used by uid/name lookup caching.

Important APIs and functions: `init_lru`, `check_lru_name`, `check_lru_uid`, and `destroy_lru` are exercised directly. `free_name` is supplied as the value cleanup callback.

Control flow and state: the test creates a two-entry queue, inserts two names, manually backfills `uid` values and uid hash slots, then verifies uid lookups hit existing nodes and increment `hits`. It then checks a missing uid allocates/returns a node with no name and increments `misses`.

Dependencies and integration: includes private `lru.h`, so it is coupled to internal `Queue`, `QNode`, and hash layout rather than public auparse APIs.

Risks and test signals: useful for catching cache accounting and lookup behavior, but fragile against internal layout refactors because it writes `q->uid_hash->array` directly. Passing is silent except for process exit zero.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/lru_cache_test.c -->
