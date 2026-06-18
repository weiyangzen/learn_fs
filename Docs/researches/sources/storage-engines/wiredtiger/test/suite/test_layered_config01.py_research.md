# sources/storage-engines/wiredtiger/test/suite/test_layered_config01.py

Purpose: verifies layered table metadata disables logging even when the connection has logging enabled.

Important APIs/types/functions: `test_layered_config01` uses `disagg_test_class`, `gen_disagg_storages`, `make_scenarios`, `session.create`, and a `metadata:create` cursor. It covers both explicit `layered:` URI creation and `table:` creation with `block_manager=disagg,type=layered`.

Control flow: the test loops over two layered URIs, appending disaggregated layered configuration for the `table:` URI, creates both tables, then calls `check_metadata_cursor`. That helper opens `metadata:create`, searches each URI, and asserts the metadata value contains `log=(enabled=false)`.

State and persistence behavior: persistent state is the table metadata string created by WiredTiger. It confirms local logging configuration is overridden/normalized for layered tables.

Dependencies/integration points: metadata cursor behavior, layered create configuration normalization, and disaggregated storage scenario setup.

Risks: string containment is simple and may not detect duplicate/conflicting log entries if metadata formatting changes. It does not write/read table data.

Test signals: pass means both layered URI styles record logging disabled in create metadata.
