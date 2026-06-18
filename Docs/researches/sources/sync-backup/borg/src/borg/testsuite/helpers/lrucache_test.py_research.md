# sources/sync-backup/borg/src/borg/testsuite/helpers/lrucache_test.py

Purpose: tests Borg's small `LRUCache` mapping and disposal hook.

Important APIs and control flow: `test_lrucache` inserts three keys into a capacity-2 cache, checks eviction, membership, `items`, indexing, `get` with default, deletion, and clearing. `test_dispose` stores temporary files with a dispose callback and asserts evicted, deleted, and cleared values are closed while retained values are not.

State and persistence: in-memory cache state plus temporary file handles that reveal disposal state.

Dependencies and integration points: depends on `helpers.lrucache.LRUCache` and `TemporaryFile`. LRU behavior is used for file descriptor/object caching.

Risks: disposal side effects must run exactly once for removed values and not for retained values. Access order versus insertion order is part of cache semantics.

Test signals: expected retained key set, `KeyError`, default lookup, and file `.closed` transitions.
