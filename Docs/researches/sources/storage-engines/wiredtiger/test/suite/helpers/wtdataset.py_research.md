<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/wtdataset.py -->
# sources/storage-engines/wiredtiger/test/suite/helpers/wtdataset.py

Purpose: Reusable test dataset abstractions for creating, populating, updating, and verifying simple and complex WiredTiger tables with optional indexes, column groups, timestamped writes, and tiered-storage population split points.

Important APIs and types: `BaseDataSet`, `SimpleDataSet`, `SimpleIndexDataSet`, `ComplexDataSet`, `TrackedComplexDataSet`, `TrackedSimpleDataSet`, and helpers `simple_key`, `simple_value`, `complex_key`. Core methods include `create`, `open_cursor`, `truncate`, `store_range`, `fill`, `populate`, `key_by_format`, `value_by_format`, `check`, `check_cursor`, and tracked `store_count`.

Control flow: A dataset is constructed with a testcase, URI, row count, formats, and config. `populate` optionally creates schema, fills rows through a timestamped cursor, and creates post-fill indexes when needed. `store_range` can force `flush_tier` or reopen the connection at hook-provided row percentages. `check` scans the cursor and delegates format-specific verification.

State and persistence behavior: The classes create tables, indexes, and colgroups in WiredTiger metadata and insert deterministic key/value rows. Tracked datasets maintain in-memory dictionaries recording how many times each key was stored, allowing expected values to vary across updates and large-value multipliers. Timestamped cursors may wrap every mutation in timestamped transactions when the timestamp hook supplies a generator.

Dependencies and integration points: Integrates with `wttimestamp.TimestampedCursor`, `WiredTigerTestCase` platform APIs for timestamps and tiered percentages, and many suite tests that need canonical data fixtures.

Risks: In-memory tracked state is authoritative for verification and can diverge if a test mutates data outside the dataset object. Tiered hook reopen behavior closes cursors mid-population and depends on testcase connection lifecycle. Complex index/colgroup assumptions are sensitive to schema-string changes.

Test signals: Exact key order, row counts, value equality, index lookup correctness, and tracked dictionary exhaustion verify data integrity.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/wtdataset.py -->
