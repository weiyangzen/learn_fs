# sources/storage-engines/tikv/tests/integrations/import/test_apply_log.rs

## sources/storage-engines/tikv/tests/integrations/import/test_apply_log.rs

Purpose: tests the import service `apply` path for plain log/SST-like files, rewrite rules, resource guards, write-CF transaction source tagging, and repeated application.

Important APIs: `ApplyRequest`, `LocalStorage`, `make_plain_file`, `register_range_for`, `rewrite_for`, `local_storage`, `check_applied_kvs_cf`, `new_cluster_and_tikv_import_client`, `disk::set_disk_status`, failpoints `mock_memory_usage`/`mock_memory_limit`, `Write`/`WriteRef`, and CF constants `CF_DEFAULT`/`CF_WRITE`.

Control flow: `test_basic_apply` creates a local file with four KVs, registers a subrange, applies a rewrite from `k` to `r`, and expects only in-range rewritten default-CF KVs. `test_apply_write_cf_sets_txn_source` writes a serialized MVCC `Write` into write CF, applies it, reads the rewritten key from engine, and checks the Lightning physical import bit is ORed into `txn_source`. `test_apply_full_resource` simulates almost-full disk and high memory via failpoints, expecting error responses. `test_apply_twice` applies the same file twice under different rewrite rules and verifies both rewritten outputs coexist.

State and persistence: temporary local storage files are read by import apply; data is persisted to the cluster engine and inspected through client helpers or direct engine reads. Global disk status and failpoints are reset.

Dependencies and integration points: import service, external/local storage, disk/memory guards, MVCC write encoding, CDC transaction source semantics. Risks include global failpoint cleanup, disk status leakage, and exact error text. Test signals are applied KV equality, txn source bit, and resource error messages.
