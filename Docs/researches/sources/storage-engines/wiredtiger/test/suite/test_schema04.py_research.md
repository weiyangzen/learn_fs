<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_schema04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_schema04.py

Purpose: verifies secondary indexes with duplicate keys, including indexes created before, during, and after table population.

Important APIs/types/functions: `test_schema04` uses `TieredConfigMixin`, `make_scenarios`, `session.create`, table/index cursors, and helpers `create_indices`, `populate`, and `check_entries`. Scenarios vary `create_index` as before first population, between two population phases, or after all rows are inserted.

Control flow: create `table:schema04` with integer primary key and six integer value columns. Populate rows in two halves with multiplication-table values modulo 100, create six single-column indexes at the scenario-selected time, then iterate the table and for each row search the corresponding duplicate index key until the matching value tuple is found.

State and persistence behavior: the primary table owns deterministic duplicated value distributions. Index state may be created empty, partially populated, or backfilled after full population, validating index maintenance across all lifecycle points.

Dependencies/integration points: covers duplicate secondary keys, index backfill, tiered storage scenarios, and cursor traversal through duplicate index entries. Risks include relying on scan-forward among duplicates; test signals are exact primary row/value checks and finding every expected value through each index.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_schema04.py -->
