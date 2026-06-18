# sources/storage-engines/wiredtiger/test/suite/test_debug_mode03.py

Purpose: verifies `debug_mode=(table_logging=true)` causes file-backed table updates to appear in WiredTiger log records, including timestamped operations.

Important APIs and control flow: helper `timestamp(kind, ts)` formats timestamps. `add_data` writes binary values, `add_data_at_ts` commits data at a timestamp, and log-scanning helpers read `WiredTigerLog.*` files looking for value bytes or packed timestamp encodings. Test cases cover table logging enabled, disabled by reconfigure, and timestamp-bearing log records.

State and persistence: real log files are the primary persisted artifact. The table itself is a file URI with binary `value_format`.

Dependencies and integration: uses `struct` to build byte patterns, `wttest`, logging configuration, timestamps, and `conn.reconfigure`.

Risks and test signals: binary log parsing is sensitive to record encoding changes. Passing tests show table logging includes expected data when enabled and stops after `debug_mode=(table_logging=false)`.
