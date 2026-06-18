# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ClusterConnectionMemoryRecord.h

Purpose: Declares an in-memory `IClusterConnectionRecord` implementation for clients/tests that need a connection string record without durable cluster-file backing.

Important APIs/types/functions: The constructor stores a `ClusterConnectionString`, marks persistence as unnecessary, and assigns a deterministic-random `UID` for display/location. It overrides `setAndPersistConnectionString()`, `getStoredConnectionString()`, `upToDate()`, `getLocation()`, `makeIntermediateRecord()`, `toString()`, and protected `persist()`.

Control flow: Callers construct the record with a known connection string. Updates modify in-memory state; `persist()` is a no-op returning success. `upToDate()` always reports true and returns the in-memory connection string because there is no external storage.

State and persistence behavior: All state is process-local. The `UID id` only distinguishes records in logs/locations. No cluster-file write occurs, and connection string changes vanish when the record is destroyed.

Dependencies and integration points: Uses `CoordinationInterface.h` abstractions, Flow references, and deterministic random UID generation. Useful in tests, internal clients, and code paths where coordinators are supplied directly.

Risks: Because `upToDate()` always succeeds, this record cannot detect coordinator changes from persistent storage. Accidentally using it where a durable cluster file is expected can break reconnection across process restarts. The generated id is diagnostic only and not a stable identity.

Test signals: In-memory update/read behavior; no-op persist success; `makeIntermediateRecord()` copy with different connection string; location/toString include type and id; connection setup without any filesystem access.
