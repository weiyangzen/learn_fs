# sources/storage-engines/foundationdb/fdbserver/logsystem/include/fdbserver/logsystem/LogSystemFactory.h

## Purpose
Declares convenience factory functions that construct `LogSystem` or `LogSystemConsumer` instances from `ServerDBInfo`, `LogSystemConfig`, old log-system config, or recovery epoch state.

## Important APIs, Types, And Functions
Functions include `makeLogSystemFromServerDBInfo()`, `makeLogSystemConsumerFromServerDBInfo()`, `makeLogSystemFromLogSystemConfig()`, `makeOldLogSystemFromLogSystemConfig()`, and `recoverAndEndLogSystemEpoch()`.

## Control Flow
Callers pass database ID, locality, core DB info/config, optional recovered-at behavior, remote-log exclusion, and an actor collection stream. Factories delegate to static `LogSystem` constructors and `recoverAndEndEpoch()` so callers do not manually select the constructor path.

## State And Persistence Behavior
The header owns no state. Returned log systems carry epoch/core-state-derived state, and `recoverAndEndLogSystemEpoch()` writes through the recovery flow implemented by `LogSystem`.

## Dependencies And Integration Points
Depends on `LogSystem.h`. Search references show use in TLog server data setup, commit proxy, GRV proxy, resolver, backup worker, range backup worker, and cluster recovery.

## Risks And Edge Cases
Factory defaults (`useRecoveredAt=false`, `excludeRemote=false`) matter for recovery and backup callers. Passing incorrect locality or old/current config choice can cause log consumers to read the wrong generation or include/exclude remote logs incorrectly.

## Test Signals
Signals are primarily downstream: successful proxy/resolver/TLog startup, recovery from `ServerDBInfo`, and backup/range-backup log reads. `LogSystemFactory.cpp` is the implementation target for direct factory behavior.
