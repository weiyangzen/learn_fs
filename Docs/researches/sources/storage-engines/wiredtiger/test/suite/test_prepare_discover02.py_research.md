# sources/storage-engines/wiredtiger/test/suite/test_prepare_discover02.py

Purpose: validates the commit path for a prepared transaction discovered from a preserved backup checkpoint, including timestamped read visibility before and after the commit timestamp.

Important APIs and types: `prepared_discover:`, `claim_prepared_id`, `commit_transaction(commit_timestamp=...,durable_timestamp=...)`, `wiredtiger.WT_NOTFOUND`, timestamped read transactions, and backup/open helpers.

Control flow: after writing committed keys 1-2 at timestamp 60, it prepares keys 3-5 with id 123 at timestamp 100, advances stable, checkpoints, backs up, and opens the backup. It discovers and claims id 123, commits it at commit timestamp 200/durable 210, then reads at timestamp 60 and 200.

State and persistence behavior: before commit timestamp 200, only the original committed keys must be visible. At read timestamp 200, the prepared keys become committed and visible. The test exercises persisted prepared metadata and subsequent visibility in the same reopened backup home.

Dependencies and integration points: tied to `preserve_prepared=true`, precise checkpoints, backup copying, and timestamp visibility rules in the storage engine.

Risks: loops for read checks set constant keys inside the loop in the source, so the test verifies representative values rather than every intended key. The primary signal remains commit visibility of the discovered prepared transaction.

Test signals: exactly one discovered id, no duplicate claims, `WT_NOTFOUND` for keys 3-5 at timestamp 60, and successful reads of prepared values at timestamp 200.
