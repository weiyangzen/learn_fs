# sources/storage-engines/wiredtiger/test/suite/helpers/error_info_util.py

Purpose: tiny assertion helper for tests of WiredTiger's last-error reporting.

Important APIs and control flow: `error_info_util` extends `wttest.WiredTigerTestCase`. `assert_error_equal()` calls `self.session.get_last_error()` and compares the top-level error, sub-level error, and message to expected values.

State and persistence behavior: reads per-session last-error state only; no filesystem/database mutation.

Dependencies and integration points: depends on the Python WiredTiger session binding exposing `get_last_error()`. Used by `test_error_info` style tests.

Risks: exact error message comparison is brittle across wording changes and localization-like edits. It assumes the session object is the one that observed the relevant error.

Test signals: all three returned fields must match expected values exactly.
