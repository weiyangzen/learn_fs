<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cursor04.py

Purpose: tests `search` and `search_near` semantics for row and column tables, including deleted keys and endpoint behavior.

Important APIs and control flow: creates 20 records with row or record-number keys, verifies direct cursor indexing for an existing key and `KeyError` for a missing key, checks `search_near` beyond the end returns the previous key, checks exact matches return 0, deletes keys 0, 5, 9, and 10, then verifies `search_near` around deleted positions returns valid neighboring keys using `expect_either()`.

State, persistence, and dependencies: state is a small table with selected tombstones. Dependencies are `wiredtiger`, `wttest`, `make_scenarios`, cursor `set_key`, `search_near`, `remove`, and record-number conversion.

Integration points: covers search positioning and compare-return semantics after deletions across row and column access methods.

Risks and test signals: `search_near` may legally choose either neighbor for gaps, so the test accepts both. Failures show incorrect boundary positioning, deleted-key visibility, or compare code handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor04.py -->
