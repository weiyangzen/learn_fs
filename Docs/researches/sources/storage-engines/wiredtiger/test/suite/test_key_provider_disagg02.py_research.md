# sources/storage-engines/wiredtiger/test/suite/test_key_provider_disagg02.py

Purpose: ensures a crash during checkpoint key rotation does not corrupt persisted key-provider metadata.

Important APIs and functions: decorated with `@disagg_test_class`; scenarios cover crash trigger points `before_key_rotation`, `during_key_rotation`, and `after_key_rotation`. It extends `suite_subprocess` to run `subprocess_func` in a child. SQLite helper `sqlite_fetch_shared_meta` reads the latest turtle metadata and optionally writes it to `key_provider.results`.

Control flow: the child populates a layered dataset, checkpoints, records shared metadata, then checkpoints with `debug=(checkpoint_crash_trigger_point=...)`, which is expected to crash/fail. The parent runs this subprocess, reopens/recoveries the home, fetches current metadata, and compares page id, LSN, and version against the pre-crash recorded metadata.

State and persistence behavior: key rotation during checkpoint must be atomic with respect to shared metadata. After crash recovery, metadata must remain at the last consistent pre-crash state.

Dependencies and integration points: integrates checkpoint crash debug hooks, key-provider extension, disaggregated PALite storage, subprocess crash harness, SQLite inspection, and recovery.

Risks and edge cases: crash trigger names are internal contracts. Regex parsing of page data and result-file handoff are brittle but direct.

Test signals: after recovery, page id, LSN, and version match the saved pre-crash metadata for each crash point.
