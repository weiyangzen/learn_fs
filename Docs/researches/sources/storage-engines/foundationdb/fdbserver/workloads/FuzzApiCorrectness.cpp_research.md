# sources/storage-engines/foundationdb/fdbserver/workloads/FuzzApiCorrectness.cpp

Purpose: Defines `FuzzApiCorrectness`, a brittle but broad random API fuzzer for thread-safe transactions, key/value limits, special keys, system-key access, conflict ranges, watches, atomic ops, transaction options, and error contracts.

Important APIs/types/functions: `ExceptionContract`, `FuzzApiCorrectnessWorkload`, `BaseTest`, `BaseTestCallback`, test cases `TestSetVersion`, `TestGet`, `TestGetKey`, `TestGetRange0..3`, `TestGetAddressesForKey`, `TestAddReadConflictRange`, `TestAtomicOp`, `TestSet`, `TestClear0..2`, `TestWatch`, `TestAddWriteConflictRange`, `TestSetOption`, and `TestOnError`.

Control flow: Constructor randomizes key layout, system/special-key modes, density, clear sizes, and registers test cases once. Setup creates a `ThreadSafeDatabase`. `loadAndRun` initializes random data batches, then repeatedly runs `randomTransaction`. Each random transaction creates many asynchronous operations, waits for random subsets, waits for all, and commits; operation-specific classes create futures or callbacks and validate expected/possible/forbidden errors.

State and persistence behavior: Persistent data is randomized user/system key data, with protected system ranges avoided for writes. Runtime state includes operation id, created tenant placeholders, key prefix map, and success. `writeBarrier` clears `normalKeys` with a system-key conflict to prevent cancelled write-only reordering.

Dependencies/integration: It uses thread-safe Native API wrappers, transaction options, special key modules, client/server knobs, mutation option metadata, protected system key definitions, deterministic randomness, and Flow futures.

Risks: The file itself documents tenant-era brittleness. Some generated operations intentionally exceed limits. Expected error contracts must track evolving API semantics; otherwise valid behavior can be reported as failure. Large random values/keys can produce large packet traces, remapped to info.

Test signals: Unexpected errors are emitted as severity error from each `Test*` contract; required-but-missing errors are also traced. `FuzzLoadAndRunError`, ignored operation warnings, and final `check()` success are the main guard outputs.
