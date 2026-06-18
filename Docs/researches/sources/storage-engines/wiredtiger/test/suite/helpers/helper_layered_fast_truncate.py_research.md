# sources/storage-engines/wiredtiger/test/suite/helpers/helper_layered_fast_truncate.py

Purpose: shared helper mixin for layered fast truncate tests on disaggregated/layered tables.

Important APIs and control flow: utility functions concatenate iterables and create inclusive ranges. `LayeredFastTruncateConfigMixin` builds table create config, opens auto-closing cursors, populates keys in one transaction, sets up leader and follower roles, truncates bounded or whole URI ranges in transactions, scans visible keys forward/backward, searches keys or `search_near`, performs leader checkpoints with stable/oldest timestamps, steps up a follower, opens an additional follower connection, searches at a read timestamp, evicts key ranges, and reads statistics.

State and persistence behavior: creates layered/disaggregated tables, writes rows, checkpoints, reopens/switches disaggregated connections, truncates ranges, evicts pages, and opens follower homes.

Dependencies and integration points: assumes the test class provides `self.uri`, `self.session`, transaction context manager, disaggregated helper methods, timestamp formatting, and extension config. Uses `wiredtiger.WT_NOTFOUND`.

Risks: tightly bound to layered table/disaggregated test infrastructure. `open_follower()` uses fixed home name `follower`, which can collide if tests share working directories. Eviction uses debug cursor config and fixed read timestamp 10.

Test signals: visible key lists, `key_exists`, `search_near_key`, timestamped reads, follower advancement, and statistics reads support assertions around fast truncate correctness.
