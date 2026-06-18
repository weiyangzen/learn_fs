# sources/storage-engines/wiredtiger/test/cppsuite/tests/api_instruction_count_benchmarks.cpp

## Purpose
Defines a cppsuite benchmark test that counts hardware instructions for selected WiredTiger cursor and session API calls under controlled low-noise conditions.

## Important APIs, Types, And Functions
`class api_instruction_count_benchmarks : public test` overrides `custom_operation`. It uses `instruction_counter` instances for transaction begin/commit/rollback, cursor insert/update/modify/remove/reset/search, open cursor cached/uncached, and `timestamp_transaction_uint`.

## Control Flow
The constructor initializes default operation tracking. `custom_operation` asserts one collection and in-memory mode, opens one cursor, extracts raw `WT_CURSOR *` and `WT_SESSION *`, then measures APIs one by one with carefully prepared cursor/transaction state. It avoids measuring implicit search work where possible by positioning the cursor before update/modify/remove, toggles cursor caching for open-cursor measurements, and closes explicitly opened raw cursors.

## State And Persistence Behavior
The test mutates one in-memory collection while measuring operations. It uses normal transaction calls for benchmark setup and cleanup. Metrics are recorded when instruction counter objects are destroyed at the end of `custom_operation`.

## Dependencies And Integration Points
Depends on `constants`, `logger`, `test`, and `instruction_counter`. It relies on cppsuite population to create data before custom operation runs and on in-memory WiredTiger config to reduce I/O and background server noise.

## Risks And Test Signals
Requires Linux perf event availability and permissions. It assumes background noise is minimized by config. Because each counter stores one value, repeated measurements are not averaged. Correct signals are successful `testutil_check` calls and generated `<api>_instructions` metrics.
