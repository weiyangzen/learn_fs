<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp25.py -->
# sources/storage-engines/wiredtiger/test/suite/test_timestamp25.py

Purpose: Checks short timestamp query aliases for compatibility with full query names.

Important APIs/types/functions: `test_timestamp25` extends `WiredTigerTestCase` and `suite_subprocess`. It calls `conn.query_timestamp` with `get=all_durable`, `get=all_durable_value`, `get=oldest_reader`, `get=oldest_reader_value`, `get=oldest_timestamp`, `get=oldest_timestamp_value`, `get=pinned`, `get=pinned_timestamp`, `get=stable_timestamp`, and `get=stable_timestamp_value`.

Control flow: The test issues pairs of equivalent query names and asserts each pair returns the same string timestamp. It does not need data setup because it is testing API name mapping rather than timestamp movement.

State and persistence behavior: No table state is created. It reads current connection timestamp metadata and validates query dispatch aliases.

Dependencies and integration points: Integrates the Python binding with WiredTiger's timestamp query parser and backwards-compatible option names.

Risks: Low behavioral complexity, but a parser rename or alias removal could break existing applications even if timestamp internals are correct.

Test signals: Equality assertions between canonical and short/alternate query names.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp25.py -->
