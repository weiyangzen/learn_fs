# sources/storage-engines/wiredtiger/test/suite/test_layered_delta15.py

Purpose: randomized high-volume internal page delta coverage across encryption, compression, URI type, timestamped/non-timestamped operation, and delta configuration scenarios.

Important APIs and functions: `test_layered_delta15` uses `DisaggConfigMixin`, palite page log, compressor/encryptor extensions, URI scenarios for layered and file tables, `page_delta` variants including leaf-only and none, 10,000-item randomized key/value sets, `stat.conn.rec_page_delta_internal`, `rec_page_delta_leaf`, and `cache_read_internal_delta`.

Control flow: the test creates a small-page table, inserts many randomized records, checkpoints, applies a randomized subset of modifications with optional commit timestamps, checkpoints again, verifies stats according to delta mode, reopens, and validates all expected values against the initial state plus modifications.

State and persistence behavior: the file stresses realistic random internal-tree shapes and values. Timestamped mode requires stable timestamp advancement before checkpoints; non-timestamped mode verifies latest state. Reopen forces reconstruction from stored images/deltas under compression and encryption combinations.

Dependencies and integration: integrates page-log delta encoding, random workload generation, compression/encryption, layered/file disaggregated URIs, timestamp logic, and stats. Risks include nondeterministic flakiness from random data, encoded delta corruption under compression/encryption, internal-delta reads when disabled, and large scenario runtime. Test signals are statistic expectations per delta mode and full data verification.
