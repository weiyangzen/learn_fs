<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_follower01.py

Purpose: validates that a disaggregated follower can use the ingest component of a layered table without any stable component.

Important APIs/types/functions: class `test_layered_follower01` derives from `wttest.WiredTigerTestCase`, uses `@disagg_test_class`, `gen_disagg_storages`, `make_scenarios`, `wiredtiger.Modify`, `WT_NOTFOUND`, cursor scans, `largest_key`, and `next_random=true`.

Control flow: the connection starts as `disaggregated=(role="follower")`. Tests create a layered table, write only follower-local ingest records, and then exercise forward scan, reverse scan, modify operations, search and `search_near` on missing/found keys, `largest_key`, and random cursors. `test_secondary_modifies_without_stable` updates every tenth value via `cursor.modify`.

State and persistence behavior: all data lives in the follower ingest table; no stable checkpoint data is required. The test checks that reads, writes, modifies, and cursor navigation work in this ingest-only state.

Dependencies/integration points: integrates layered cursor APIs with the follower role, timestamped commits, and value modification. Risks are large loop cost (`nitems=10000`) and assumptions about lexical largest key among `"Hello"`, `"Hi"`, and `"OK"` prefixes. Test signals are item counts, exact modified values, search return codes, largest key, and random key prefix.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower01.py -->
