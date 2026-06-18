# sources/storage-engines/foundationdb/fdbserver/workloads/AtomicOpsApiCorrectness.cpp

Purpose: defines `AtomicOpsApiCorrectness`, a focused API-level correctness workload for individual atomic operations. It checks how each atomic mutation behaves on existing keys, missing keys, empty values, read-your-writes visibility, and legacy API version 500 semantics.

Important APIs, types, and functions: `AtomicOpsApiCorrectnessWorkload` extends `TestWorkload`; `opType` selects the operation under test and `testFailed` reports check status. Shared helper actors include `testAtomicOpSetOnNonExistingKey()`, `testAtomicOpUnsetOnNonExistingKey()`, `testAtomicOpOnEmptyValue()`, `testAtomicOpApi()`, and `testCompareAndClearAtomicOpApi()`. Operation-specific actors are `testMin`, `testMax`, `testAnd`, `testOr`, `testXor`, `testAdd`, `testCompareAndClear`, `testByteMin`, and `testByteMax`.

Control flow: `start()` dispatches exactly one operation test, or randomly chooses one if `opType=-1`. Each helper clears or seeds a key, commits a transaction containing an atomic operation, waits briefly, then reads the key in a separate transaction and in a same-transaction read-your-writes path. Numeric helpers compare little-endian `uint64_t` values; byte helpers compare `StringRef` byte ordering; compare-and-clear expects the key to disappear when absent or equal and remain when unequal. If an unexpected value appears, the helper logs a `SevError` trace and sets `testFailed`.

State and persistence behavior: test keys are deterministic per client (`test_key_*_<clientId>`). The workload mutates only those user keys and clears/reuses them between cases. No metadata or external persistence is involved. For current API behavior, atomic operations on absent keys generally initialize from or preserve the operand according to the operation; for API 500 compatibility, `Min` and `And` explicitly validate older missing-key semantics.

Dependencies and integration points: uses `ReadYourWritesTransaction`, `runRYWTransaction`, `runRYWTransactionNoRetry`, `FDBTransactionOptions::RAW_ACCESS`, transaction atomic APIs, and `getApiVersion()/setApiVersion()` for legacy compatibility. It registers as a tester workload and emits trace events under `AtomicOpCorrectnessApiWorkload`.

Risks and edge cases: lambdas encode expected semantics in the test itself, so changes in API-version rules must update these expectations. The code assumes eight-byte numeric operands for most operations and asserts returned sizes. Empty-value behavior is randomized between clearing and setting an empty value, which improves coverage but makes specific subcase selection seed-dependent.

Test signals: `check()` returns `!testFailed`. Diagnostic trace events include `AtomicOpApiCorrectnessUnexpectedOutput`, `AtomicOpSetOnNonExistingKeyUnexpectedOutput`, `AtomicOpUnsetOnNonExistingKeyUnexpectedOutput`, and `AtomicOpOnEmptyValueUnexpectedOutput`.
