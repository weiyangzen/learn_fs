# sources/storage-engines/wiredtiger/test/suite/test_layered_config04.py

Purpose: verifies creating a layered table with logging explicitly enabled is rejected with a clear error.

Important APIs/types/functions: uses `assertRaisesWithMessage`, `wiredtiger.WiredTigerError`, `session.create`, and disaggregated scenarios. Connection role is leader.

Control flow: the single test attempts to create `layered:test_layered_config04` with `key_format=S,value_format=S,log=(enabled=true)` and expects a `Logging is not supported for layered` error.

State and persistence behavior: no table should be created and no durable layered metadata should be accepted for an unsupported logged configuration.

Dependencies/integration points: configuration validation for layered tables, error propagation through Python API, and disaggregated test setup.

Risks: scenario generator name references `test_layered_eviction02`, likely harmless but confusing for test identity. The assertion is regex/string dependent.

Test signals: pass means unsupported logged layered tables fail at create time with the expected diagnostic.
