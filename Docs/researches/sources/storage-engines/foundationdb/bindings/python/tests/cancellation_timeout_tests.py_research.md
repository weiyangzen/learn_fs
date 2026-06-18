# sources/storage-engines/foundationdb/bindings/python/tests/cancellation_timeout_tests.py

Purpose: This file is a focused Python binding test suite for transaction cancellation, retry-limit, timeout, database-default retry/timeout, and combined behavior.

Important APIs and types: It uses `fdb.FDBError`, transaction options `set_timeout` and `set_retry_limit`, database options `set_transaction_timeout` and `set_transaction_retry_limit`, `cancel`, `reset`, `on_error`, `commit`, and basic mutation/read operations. `retry_with_timeout` wraps individual checks with a guard transaction timeout.

Control flow: Each test defines small transactional scenarios that deliberately trigger cancellation, retryable `transaction_too_old` errors, future-version errors, or timeout expiry. Assertions inspect exact FoundationDB error codes such as `1025` canceled, `1031` timed out, `1007` retryable, and `1009` future version.

State and persistence behavior: Tests write simple keys such as `foo` but mainly validate transaction-local state: whether cancellation survives `on_error`, whether reset clears cancellation/timeouts/retry counts, and whether database defaults are reapplied after reset. The suite resets database-level options to defaults at the end of affected tests.

Dependencies and integration points: It depends on the Python binding option wrappers generated in `impl.py`, C API transaction state, time-based behavior, and `unit_tests.py` as the orchestrator.

Risks: Time-based sleeps can be slow or flaky on overloaded systems. The retry wrapper creates a timeout transaction but retries the tested transaction separately, so unexpected errors can loop until timeout. Exact error-code expectations bind tightly to FoundationDB C API semantics.

Test signals: Strong signals are exact error-code matches across cancellation, retry-limit exhaustion, transaction reset, database-default override, timeout retroactivity, timeout unset behavior, and combined cancellation/retry-limit cases.
