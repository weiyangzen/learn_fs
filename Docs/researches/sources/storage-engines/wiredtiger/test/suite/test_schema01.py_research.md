<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_schema01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_schema01.py

Purpose: verifies basic table, column group, and cursor behavior across empty/recreated schema lifecycle and reopen boundaries.

Important APIs/types/functions: `test_schema01` extends `TieredConfigMixin` and `WiredTigerTestCase`; it uses `gen_tiered_storage_sources`, `make_scenarios`, `session.create`, `dropUntilSuccess`, and table cursors. Static inputs `pop_data` and `expected_out` define country/year/population rows and expected padded string-key ordering.

Control flow: for both no-reopen and reopen cases, create a table with `key_format=5s`, `value_format=HQ`, named columns, and two column groups; insert records via overwrite cursor; optionally reopen the connection; iterate the table; compare stringified rows to expected order; then drop the table.

State and persistence behavior: the reopen scenario verifies schema metadata, column group metadata, padded fixed-size string keys, and records survive close/reopen. The repeated create/drop loop checks cleanup before recreation.

Dependencies/integration points: covers tiered scenario generation, column-group table mappings, fixed-width string keys, `dropUntilSuccess`, and cursor iteration. Risks include expected string formatting being tightly coupled to Python binding display; test signals are exact row order/value strings and successful table drops.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_schema01.py -->
