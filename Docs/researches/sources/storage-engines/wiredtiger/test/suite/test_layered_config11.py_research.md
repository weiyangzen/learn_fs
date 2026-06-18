# sources/storage-engines/wiredtiger/test/suite/test_layered_config11.py

Purpose: intended to test read/write behavior across leader-to-follower step-down with compression and encryption combinations, but currently skips because step-down is unsupported.

Important APIs/types/functions: uses `DisaggConfigMixin`, scenario matrices for encryptors `none`/`rotn` and compressors `none`/`snappy`, extension loading for compressors/encryptors, transaction sync fsync, and disaggregated storage scenarios.

Control flow: the only test immediately calls `skipTest('Step-down is not supported yet.')`. Dormant logic would create a layered table with selected block compressor, insert 10,000 rows, checkpoint, reopen as follower, and verify all rows.

State and persistence behavior: if enabled, it would validate compressed/encrypted disaggregated checkpoint persistence through role transition. Currently no table state is created.

Dependencies/integration points: compressor/encryptor extension loading, page-log/disaggregated configuration, checkpointing, and follower reopen behavior.

Risks: currently no runtime behavioral coverage. When step-down support arrives, the dormant code may need checkpoint metadata pickup or updated role-transition semantics.

Test signals: active signal is skip only; future pass would show encrypted/compressed layered data can be read after step-down/reopen.
