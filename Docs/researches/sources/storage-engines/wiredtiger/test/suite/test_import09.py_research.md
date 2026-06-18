# sources/storage-engines/wiredtiger/test/suite/test_import09.py

Purpose: tests table import with `repair=true` and no exported metadata across table layouts, allocation sizes, compressors, and encryptors. It is skipped under tiered storage.

Important APIs and functions: scenarios combine simple/named-column table definitions, allocation sizes, compressors, and encryptors. `conn_extensions` loads compression/encryption extensions, and `conn_config` sets destination encryption parameters.

Control flow: the test creates/populates unrelated data, creates `table:original_db_table` with scenario storage options, writes/checkpoints two batches, exports table/file metadata only for later comparison, closes, opens `IMPORT_DB`, populates unrelated data, advances oldest timestamp, copies the `.wt` file, imports with `import=(enabled,repair=true)`, verifies, checks imported rows, compares reconstructed file and table metadata to originals, appends remaining rows, and checkpoints.

State and persistence behavior: repair import must reconstruct both table and file metadata from the copied file while preserving storage options and named-column schema.

Dependencies and integration points: integrates extension loading, table repair import, metadata comparison, and data verification. It reuses helper logic from `test_import01`.

Risks and edge cases: test matrix is large and extension-dependent. Random values are generated for simple table scenarios. Tiered storage is excluded because backing-file assumptions do not hold.

Test signals: successful import and verification, equivalent reconstructed metadata, preserved rows, and successful post-import writes.
