# sources/storage-engines/foundationdb/fdbserver/logsystem/LogSystemRecoveryTests.cpp

## Purpose
Provides focused Flow unit tests for `getRecoverVersionUnicast()`, the version-vector/unicast recovery-version calculation declared in `LogSystem.h` and implemented in `LogSystem.cpp`.

## Important APIs, Types, And Functions
`makeSingleLogSet()` builds a `LogSet` containing synthetic `TLogInterface`s. `makeLogGroupResults()` creates the tuple consumed by `getRecoverVersionUnicast()`: replication factor, `TLogLockResult` vector, and the unavailable-TLog policy result. Test cases construct `UnknownCommittedVersions` chains and assert returned `(maxKCV, recoverVersion)` tuples.

## Control Flow
Each test exits early when `SERVER_KNOBS->ENABLE_VERSION_VECTOR_TLOG_UNICAST` is disabled. Otherwise it creates local TLog interfaces, packages lock results and unknown committed versions, calls `getRecoverVersionUnicast()`, asserts that a result exists, and checks the maximum known committed version plus selected recovery version.

## State And Persistence Behavior
No persistent state is written. Test state is synthetic in-memory log-set metadata, `TLogLockResult` contents, and unknown committed version vectors. The tests intentionally vary known committed versions, replication factor, local/non-local log sets, unavailable policy flags, delivery sets, and version chains.

## Dependencies And Integration Points
The file includes `LogSystem.h` and `flow/UnitTest.h`. It indirectly validates how `LogSystem::getDurableVersion()` results are interpreted during epoch recovery, especially when version-vector unicast is enabled and recovery must decide how far beyond max KCV it can safely advance.

## Risks And Edge Cases
Covered cases include fallback to max KCV with no unknown versions, halting on missing delivery, replication-policy failure, respecting versions above max KCV, broken `prevVersion` chains, ignoring non-local extra log sets, partial availability policy failure, filtering versions at or below max KCV, and sparse/random version chains that should not skip gaps.

## Test Signals
The file is itself the test signal. Trace events with names like `SimpleTestRecoverVersionFailed` and `BrokenChainTestRecoverVersionFailed` provide detailed diagnostics before assertions fail.
