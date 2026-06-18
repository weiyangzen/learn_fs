<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_schema02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_schema02.py

Purpose: broad schema API coverage for table column declarations, column group validation, index creation order, populated and post-population index building, and data/index correctness.

Important APIs/types/functions: `test_schema02` uses `wiredtiger.WiredTigerError`, `TieredConfigMixin`, `make_scenarios`, `expect_failure_colgroup`, `populate`, `check_entries`, and `check_indices`. It builds a compound key/value schema with columns `(ikey,Skey,S1,i2,S3,i4)` and two column groups.

Control flow: negative tests assert invalid formats, bad column counts, missing table/colgroup names, invalid columns, key columns in column groups, duplicate exclusive creates, missing value-column coverage, and namespace isolation. Positive tests create indexes before and after column groups, populate 1000 rows with square/cube-derived values, create a late index, and verify primary and index cursor projections.

State and persistence behavior: schema state is entirely metadata-backed; the test stresses ordering of metadata creation and index backfill from existing data. No explicit reopen occurs, but late index creation validates durable table contents are scanned into index structures.

Dependencies/integration points: integrates schema validation, column groups, secondary indexes, compound keys, tiered scenarios, and error-message regexes. Risks include brittle error strings and floating cube-root inference; signals are expected exceptions, cursor counts, and exact value checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_schema02.py -->
