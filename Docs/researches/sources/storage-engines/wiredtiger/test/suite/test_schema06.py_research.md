<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_schema06.py -->
# sources/storage-engines/wiredtiger/test/suite/test_schema06.py

Purpose: stresses repeated secondary index creation and removal around column groups after inserting a larger dataset.

Important APIs/types/functions: `test_schema06` uses `TieredConfigMixin`, `make_scenarios`, `dropUntilSuccess`, and helpers `flip`, `unflip`, `create_index`, and `drop_index`. The active test is `test_index_stress`; `check_entries` appears to be leftover validation code for a different `table:main` shape and is not called.

Control flow: create `table:schema06` with string primary key, six string values, and two column groups. Create indexes on `s0` and `s1` around column-group creation, insert 1000 rows using digit-reversed transformed values, close the cursor, then drop both indexes.

State and persistence behavior: table data and column groups remain while index metadata and index files are created and deleted. The test is mostly about schema lifecycle cleanup rather than verifying data after drop.

Dependencies/integration points: covers schema metadata, index file creation/removal, column group interactions, tiered scenarios, and `dropUntilSuccess` retry semantics. Risks include limited final assertions and dead helper code; the main signal is absence of errors during heavy insert and index drop.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_schema06.py -->
