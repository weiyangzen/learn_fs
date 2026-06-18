# sources/storage-engines/wiredtiger/test/suite/test_hs27.py

Purpose: verifies that VLCS reconciliation does not RLE-compact adjacent identical values when their timestamps are heterogeneous. The same value may appear in adjacent cells, but timestamp boundaries must remain observable through time-travel reads.

Important APIs and functions: `test_hs27` uses `SimpleDataSet`, timestamped transactions, and `make_scenarios`. Scenario axes vary number of write timestamps (`2`, `3`, `10`), keys per timestamp (`1`, `2`, `3`), optional initialization, group ordering, and key ordering. Helpers map logical timestamp groups to physical keys (`get_writetime`, `get_readtime`, `get_key`, `invert_key`, `invert_timestamp`) and validate with `check1`, `check2`, `check3`, `check`, and `checkall`.

Control flow: the test optionally initializes the table with `value_1`, then writes `value_2` to adjacent key groups at distinct commit timestamps. It validates expected visibility across all read timestamps, forces eviction/reconciliation, and repeats validation so RLE-encoded pages are read back.

State and persistence behavior: timestamp group metadata is the state under test. Although values may be byte-identical and adjacent, each group has separate start times and must not be collapsed into one RLE run with a single time window.

Dependencies and integration points: integrates VLCS RLE, timestamp visibility, eviction, and the history-store path. It depends on the WiredTiger test transaction helpers and dataset key generation.

Risks and edge cases: ordering axes exercise forward/backward writes to catch assumptions that only ascending insertion order preserves timestamp boundaries. The test is sensitive to the exact key range around 71 and to off-by-one inversions in helper logic.

Test signals: expected scans at every generated read timestamp must match `value_1` or `value_2`; count and value mismatches indicate timestamp/RLE corruption.
