# sources/storage-engines/wiredtiger/test/suite/test_checkpoint22.py

Purpose: verifies that skipped trees during checkpoint retain and use the correct checkpoint write generation after restart, so transaction IDs on disk are unpacked with the checkpoint generation rather than the current one.

Important APIs and types: `SimpleDataSet`, checkpoint helper for named/unnamed checkpoints, `reopen_conn`, open read transactions, and transaction ID generation through many small commits.

Control flow: create two tables; churn many commits to raise transaction IDs; hold a reader transaction so later txnids are written to disk; update the main table to `value_b`; checkpoint; rollback reader and restart; update a second table so a subsequent checkpoint is non-vacuous while the first table is skipped; checkpoint again; read the first table from the second checkpoint.

State and persistence behavior: the first table is unchanged across restart and second checkpoint, so the checkpoint may skip it. The test protects persistence metadata that records the correct write generation for unpacking transaction visibility.

Dependencies and integration points: relies on restart behavior, transaction ID visibility without timestamps, checkpoint skip logic, and named/unnamed checkpoint combinations. Skipped for disaggregated and tiered hooks.

Risks: the comment notes more advanced torn-transaction variants are not practical in Python. The test assumes transaction IDs after restart are sufficiently lower than pre-restart IDs.

Test signals: reading the second checkpoint for the skipped table returns all `value_b` rows, showing checkpoint-generation visibility did not hide valid data.
