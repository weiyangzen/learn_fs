# sources/storage-engines/wiredtiger/test/suite/test_import08.py

Purpose: ensures imported files retain or reset write-generation state correctly so old transaction IDs from a different database do not hide imported records.

Important APIs and functions: scenarios cover metadata import and repair import. `parse_write_gen` extracts `write_gen=<num>` from metadata using a regex. The test uses a second session to hold a transaction ID pinned across checkpoints.

Control flow: it populates many generated tables to allocate transaction IDs, opens a second session, removes an entry inside an uncommitted transaction to pin IDs, creates the import file, writes each record at a timestamp with a checkpoint after each write to raise the btree write generation, exports metadata, rolls back the pinned transaction, copies the file to `IMPORT_DB`, opens the new home, advances oldest timestamp, imports with either metadata or repair mode, verifies, checks that metadata write generation is greater than 1, and validates all records are visible.

State and persistence behavior: pages may contain transaction IDs and write generations from the source database. Import must use the btree-specific base write generation to decide when to clear IDs in the destination.

Dependencies and integration points: integrates transaction ID visibility, checkpoint write generations, metadata parsing, import repair/metadata modes, and timestamped binary data.

Risks and edge cases: regex parsing is simple and assumes `write_gen` appears in metadata. The test intentionally manipulates transaction IDs; changes in reconciliation ID-obsolescence rules may alter setup requirements.

Test signals: imported metadata has `write_gen > 1` and all source records are visible in the fresh connection.
