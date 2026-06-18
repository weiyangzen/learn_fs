<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp17.py -->
# sources/storage-engines/wiredtiger/test/suite/test_timestamp17.py

Purpose: Tests a non-timestamped tombstone written after timestamped updates, ensuring it hides all historical versions and continues to do so as oldest timestamp advances.

Important APIs/types/functions: `test_timestamp17` uses `make_scenarios` for integer row-store and column-store keys. It relies on cursor `remove`, `search`, `WT_NOTFOUND`, `begin_transaction('no_timestamp=true')`, timestamped commits, and `conn.set_timestamp('oldest_timestamp=...')`.

Control flow: The test writes one key at timestamps 25, 50, and 200, verifies it is absent before the first update, then removes it without a timestamp. It reads at several historical and future read timestamps and expects `WT_NOTFOUND`. It then advances oldest to 49, 99, 100, and 200 while continuing to verify invisibility at relevant read timestamps.

State and persistence behavior: The key's update chain contains timestamped values followed by a globally visible no-timestamp tombstone. Oldest timestamp advancement may discard older history, but must not expose covered timestamped values.

Dependencies and integration points: Exercises transaction visibility, history-store reconciliation rules, tombstone semantics, and row/column key formats through the Python test harness.

Risks: Bugs in no-timestamp tombstone handling could resurrect historical values after history cleanup or oldest timestamp advancement. Column-store handling is especially important because recno keys have different deleted-value behavior.

Test signals: Repeated `WT_NOTFOUND` checks across read timestamps and oldest movements catch value resurrection or incorrect history truncation.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp17.py -->
