# sources/storage-engines/wiredtiger/test/suite/test_import03.py

Purpose: tests successful table import, including table metadata plus backing file metadata, for simple and named-column table layouts.

Important APIs and functions: scenarios cover a recno/integer simple table and a named-column table with value format `SSi`. It inherits data helpers from `test_import_base` and uses `metadata:` to capture both `table:` and `file:` configs.

Control flow: the test populates unrelated tables, creates `table:original_db_table`, writes/checkpoints two batches, exports table and file metadata, builds an import config combining table config and `file_metadata`, closes, opens `IMPORT_DB`, populates unrelated objects, advances oldest timestamp, copies `original_db_table.wt`, imports the table, verifies it, checks imported rows, compares table metadata, appends remaining rows, and checkpoints.

State and persistence behavior: table import must reconstruct both logical table metadata and physical file metadata. For named columns, column metadata and value layout must survive import.

Dependencies and integration points: integrates table-level import syntax, file copy, timestamp validation, `verifyUntilSuccess`, and `config_compare`.

Risks and edge cases: random sample values are generated at module/scenario creation time, which can affect reproducibility of exact values but not test invariants. It only copies one backing `.wt` file because these table forms are single-file tables.

Test signals: successful import, equivalent table metadata after stripping unique fields, correct data visibility, and successful post-import writes.
