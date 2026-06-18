# sources/storage-engines/wiredtiger/test/suite/test_layered_eviction01.py

Purpose: ensures a follower does not evict pages ahead of the materialization frontier, and that checkpoint/materialization accounting protects pages that are not yet safe to discard.

Important APIs and functions: `test_layered_eviction01` uses follower role disaggregated config, `disaggregated=(lose_all_my_data=true)`, `stat.conn.cache_eviction_ahead_of_last_materialized_lsn`, `cache_eviction_blocked_precise_checkpoint`, `cache_scrub_restore`, `checkpoint_pages_reconciled_bytes`, `conn.set_context_uint`, page-log `pl_set_last_materialized_lsn`, and a debug eviction cursor helper.

Control flow: the test creates a large layered table, writes many records, checkpoints, manipulates materialized LSN context, reads and evicts ranges with debug eviction, changes connection configuration, and asserts eviction is blocked or counted when pages are ahead of the frontier.

State and persistence behavior: the central state is page-log materialization frontier versus page LSN. Pages ahead of that frontier must remain available in cache or be restored rather than discarded, even under eviction pressure. Timestamps and checkpoints control page reconciliation.

Dependencies and integration: integrates disaggregated follower behavior, page-log frontier APIs, eviction debug hooks, statistics, and precise checkpoint interactions. Risks include data loss from evicting unmaterialized pages, stuck cache if all eviction is blocked, and incorrect frontier stat accounting. Test signals are statistic thresholds, exception assertions, and successful reads around forced eviction.
