# sources/storage-engines/wiredtiger/test/suite/helpers/eviction_util.py

Purpose: shared helper class for Python eviction tests, especially tests needing page eviction and time-window cleanup.

Important APIs and control flow: `evict_cursor_tw_cleanup()` opens a debug session with `release_evict_page=true`, begins an `ignore_prepare=true` transaction, scans keys with periodic cursor resets to trigger page release/eviction, then rolls back and closes. `get_stat()` reads a statistics cursor. `populate()` writes timestamped values in individual transactions, committing at `timestamp_str(k + 1)`.

State and persistence behavior: writes records to target URIs and uses debug session settings to influence eviction behavior. Reads connection/data-source statistics.

Dependencies and integration points: extends `wttest.WiredTigerTestCase`, uses WiredTiger debug cursor/session config, statistics cursors, and timestamp helpers from the test base.

Risks: debug eviction behavior is internal and may change. The helper assumes integer keys from `0` to `nrows - 1` and that the URI supports those keys.

Test signals: expected eviction/stat counters and absence/presence of time-window cleanup effects after forced eviction.
