# sources/storage-engines/wiredtiger/test/suite/test_layered_eviction03.py

Purpose: ensures follower application threads skip eviction of pages with updates or dirty state, rather than doing unsafe app-thread eviction work in disaggregated follower mode.

Important APIs and functions: `test_layered_eviction03` uses follower disaggregated config, a small cache, random string generation, large inserted values, and `stat.conn.cache_eviction_app_threads_skip_updates_dirty_page`.

Control flow: the test creates enough data in a follower-role connection to apply cache pressure and dirty/update state. It then reads the connection eviction statistic and asserts the skip counter is greater than zero.

State and persistence behavior: follower pages with dirty updates are not supposed to be evicted by application threads. The test's state is intentionally cache-pressure-heavy and follower-local, so eviction policy should choose to skip rather than reconcile unsafe pages.

Dependencies and integration: integrates follower role eviction policy, cache pressure, random data generation, and connection statistics. Risks include app threads evicting dirty follower pages, missing skip accounting, or cache pressure behavior changing enough to make the test flaky. Test signal is a positive skip statistic.
