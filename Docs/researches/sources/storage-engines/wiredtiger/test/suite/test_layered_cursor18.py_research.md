# sources/storage-engines/wiredtiger/test/suite/test_layered_cursor18.py

Purpose: regression tests for stale alternate constituent cursor state when a single layered follower cursor is reused across transactions. It covers read timestamp changes and snapshot generation changes caused by new follower ingest writes between calls.

Important APIs and functions: `test_layered_cursor18` uses `DisaggConfigMixin` indirectly through disaggregated helpers, `wiredtiger_open` for a follower, timestamped transactions, `next`, `prev`, and assertion helpers `follow_next` and `follow_prev`. It also defines reusable snapshot-generation helpers `snapshot_gen_ingest_next` and `snapshot_gen_ingest_prev`, with test variants for explicit transaction and auto-transaction combinations.

Control flow: each scenario creates leader stable data and follower ingest data such that one constituent is selected as current while the other is left parked as an alternate. The next operation runs under a different read timestamp or after a new ingest write, and the test asserts the cursor re-searches the alternate constituent under the new snapshot before returning data.

State and persistence behavior: leader checkpoint data provides stable histories at older timestamps; follower ingest data provides newer versions or newly committed keys. The same cursor object crosses transaction boundaries, so persistence correctness depends on invalidating or refreshing cached constituent state.

Dependencies and integration: integrates with layered merge cursors, transaction snapshots, follower ingest writes, and checkpointed stable pages. Risks include returning stale values, using a parked alternate key from an older snapshot, and mismatches between explicit and implicit transaction paths. Test signals are exact key/value assertions after each `next` or `prev`, with inline comments documenting previously buggy returns.
