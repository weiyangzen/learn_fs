# sources/storage-engines/wiredtiger/test/suite/test_inmem01.py

Purpose: tests in-memory cache capacity behavior: successful inserts under capacity, failure over capacity, making space by deletes/replacements, and wedged-cache recovery behavior.

Important APIs and functions: `conn_config` enables `in_memory=true` with 5MB cache; `table_config` sets small pages. Scenarios cover recno and string-row keys. Tests use `SimpleDataSet`, large string values, `WT_CACHE_FULL`, and `sleep`.

Control flow: `test_insert` inserts a modest dataset. `test_insert_over_capacity` inserts until the cache fills and expects `WT_CACHE_FULL`. `test_insert_over_delete` fills, deletes records, then verifies inserts can proceed. `test_insert_over_delete_replace` checks replacement after deletions. `fill` is a helper for repeated inserts; `test_wedge` stresses behavior after the cache is wedged/full and then recovers after space is freed.

State and persistence behavior: because `in_memory=true`, there is no eviction-to-disk escape path for excess data. Memory accounting, deleted content reclamation, and cache-full state transitions are the main state under test.

Dependencies and integration points: depends on the WiredTiger in-memory engine, cache accounting, cursor insert/remove/update behavior, and dataset helpers.

Risks and edge cases: tests can be sensitive to cache-size/page-size accounting changes. Timing/sleep in wedge recovery may be environment-sensitive.

Test signals: expected `WT_CACHE_FULL` errors occur only when over capacity; after deletion/replacement, inserts and checks succeed.
