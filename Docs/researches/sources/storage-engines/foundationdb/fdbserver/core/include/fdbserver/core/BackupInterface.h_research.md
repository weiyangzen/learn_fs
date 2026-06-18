# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/BackupInterface.h

## sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/BackupInterface.h

Purpose: defines the RPC interface identity for backup workers.

Important type: `BackupInterface` with file identifier `6762745`, `waitFailure` stream, `LocalityData`, endpoint helpers, equality, and serialization.

Control flow and state: the interface is a value object. `id()` and `getToken()` derive identity from the `waitFailure` endpoint token; `address()` returns the endpoint primary address. `initEndpoints()` is empty because endpoint construction is handled by stream serialization/initialization elsewhere.

Dependencies and integration: depends on FDB key/types, fdbrpc streams, locality metadata, and wait-failure infrastructure. Cluster controller and backup recruitment/status paths use it to identify and monitor backup workers.

Risks and tests: identity depends entirely on `waitFailure` endpoint token, so default-constructed or uninitialized interfaces should not be used as real workers. Serialization compatibility is important for recruitment messages. Tests should verify endpoint initialization, locality propagation, equality semantics, and wait-failure liveness behavior.
