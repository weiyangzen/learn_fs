<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat10.py -->
# sources/storage-engines/wiredtiger/test/suite/test_stat10.py

Purpose: validates table-type-specific btree statistics for row-store and variable-length column-store under timestamped updates, deletes, overflow values, and eviction.

Important APIs/types/functions: `test_stat10` uses `make_scenarios` with oldest/stable timestamp constraints, `stat.dsrc.btree_entries`, `btree_row_empty_values`, `btree_column_deleted`, `btree_column_rle`, `btree_overflow`, backup block stats, and release eviction.

Control flow: create a row or VLCS table with raw-byte values, set oldest/stable to 10, insert 100 records at ts 20 with a mix of invariant values, compound values, empty row values, and overflow-sized keys/values, delete two keys at ts 30, advance oldest/stable per scenario, evict sample keys, open data-source stats, and validate each stat based on format and timestamp scenario.

State and persistence behavior: eviction is required to materialize RLE and overflow accounting. Timestamp visibility is intentionally not fully specified, so assertions encode expected current behavior separately from format-specific expectations.

Dependencies/integration points: covers row/VLCS btree encoding, timestamps, overflow, tombstones, eviction, backup stat access, and disaggregated-storage skips/adjustments. Risks include physical encoding sensitivity; signals are exact stat values by scenario.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat10.py -->
