# sources/storage-engines/foundationdb/bindings/python/tests/size_limit_tests.py

Purpose: This suite validates Python binding exposure of transaction size-limit options and approximate transaction size reporting.

Important APIs and types: It uses `@fdb.transactional`, database option `set_transaction_size_limit`, transaction option `set_size_limit`, `get_approximate_size`, conflict-key helpers, and direct item assignment.

Control flow: `test_size_limit_option` writes a 1 KiB value successfully, then expects error `2101` when database or transaction size limits are set below the operation size. It also verifies that database defaults survive `on_error`. `test_get_approximate_size` mutates a transaction and asserts approximate size grows after set, clear, read conflict, and write conflict operations.

State and persistence behavior: Tests write keys `t1` through `t4` and small conflict keys. They explicitly reset the database transaction size limit after testing to avoid contaminating later tests.

Dependencies and integration points: The file depends on option-generation in `impl.py`, C API approximate-size futures, and is called from `unit_tests.py`; it can also be run standalone with a cluster file.

Risks: Exact byte-limit behavior depends on C API accounting, and approximate size is only asserted monotonically rather than by exact values. Failure to reset database defaults would affect unrelated tests.

Test signals: Error code `2101`, successful override behavior, survival of database defaults through `on_error`, and monotonic approximate-size growth are the core signals.
