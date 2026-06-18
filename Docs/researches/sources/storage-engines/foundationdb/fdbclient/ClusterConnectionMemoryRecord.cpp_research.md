# sources/storage-engines/foundationdb/fdbclient/ClusterConnectionMemoryRecord.cpp

## Purpose

`ClusterConnectionMemoryRecord.cpp` implements a non-persistent in-memory `IClusterConnectionRecord`. It is useful for tests, simulations, or callers that already manage connection-string lifetime externally.

## Important APIs And Functions

`setAndPersistConnectionString()` just assigns `cs` and returns `Void`. `getStoredConnectionString()` returns the current in-memory string. `upToDate()` copies `cs` into the output parameter and always returns true because there is no external durable store to compare. `getLocation()` returns the generated record `id`, while `toString()` prefixes it with `memory://`. `makeIntermediateRecord()` returns a new memory record holding a modified connection string. `persist()` is a successful no-op.

## Control Flow

All operations are synchronous future completions. No retry, IO, or conflict handling is needed.

## State And Persistence

State is limited to the object's in-memory `ClusterConnectionString` and record ID. Nothing survives process lifetime, and `setAndPersistConnectionString()` can mislead callers if they assume persistence means durability rather than successful interface completion.

## Dependencies And Integration Points

The file depends on `fdbclient/ClusterConnectionMemoryRecord.h` and the shared `IClusterConnectionRecord` contract. It integrates with code paths that accept any connection record implementation and do not require a cluster file or database key.

## Risks And Test Signals

The main risk is accidental use where durable connection-string changes are expected. Tests should compare behavior against file/key records, especially `upToDate()` and `persist()` semantics, and ensure generated `memory://` identifiers are useful for trace diagnostics.
