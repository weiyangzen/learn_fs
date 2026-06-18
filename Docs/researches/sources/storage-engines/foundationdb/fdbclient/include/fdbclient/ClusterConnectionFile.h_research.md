# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ClusterConnectionFile.h

Purpose: Declares a file-backed implementation of `IClusterConnectionRecord`, the abstraction used to store, read, update, and persist the cluster connection string.

Important APIs/types/functions: Constructors load an existing cluster file or create one from a `ClusterConnectionString`. `openOrDefault()` resolves empty inputs to the default cluster file. `setAndPersistConnectionString()`, `getStoredConnectionString()`, `upToDate()`, `getLocation()`, `makeIntermediateRecord()`, `toString()`, and protected `persist()` implement the record interface. Static helpers `lookupClusterFileName()` and `getErrorString()` support default path resolution and user-facing constructor errors.

Control flow: Native API startup opens a specified or default file, parses the connection string, and stores it in memory. When coordinators forward a changed connection string, `setAndPersistConnectionString()` updates memory and writes the file. `upToDate()` rereads persistent storage to detect external modifications.

State and persistence behavior: Persistent state is the cluster file contents at `filename`; in-memory state is inherited `IClusterConnectionRecord::cs`. `makeIntermediateRecord()` creates a modified non-persisted record for connection transitions. Successful persistence is reported as a future so callers can chain actor flow.

Dependencies and integration points: Depends on `CoordinationInterface.h` for `ClusterConnectionString` and record interface. Used by native API database connection setup, cluster-file change handling, hot-standby switching, and coordinator forwarding.

Risks: File parsing and path lookup are startup-critical. Partial writes, permissions, stale external edits, or invalid cluster file format can prevent cluster connection or persist wrong coordinators. Intermediate records must not be mistaken for durable state until persistence completes.

Test signals: Default path lookup; constructor error strings for missing/unreadable/invalid files; set-and-persist then reopen; external file edit detection via `upToDate`; intermediate record behavior; connection-string forwarding updates; permission and atomic-write failure scenarios.
