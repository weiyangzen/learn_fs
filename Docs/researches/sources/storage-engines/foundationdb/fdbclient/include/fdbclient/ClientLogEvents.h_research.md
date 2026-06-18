# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ClientLogEvents.h

Purpose: Defines serialized client transaction profiling event records and trace-log emission helpers for get-version, get, get-range, commit, and error paths. The file explicitly marks these structures as persistent internal FDB format, so schema changes can break upgrade simulation and old metadata replay.

Important APIs/types/functions: `FdbClientLogEvents::EventType` classifies persisted events. `TransactionPriorityType` is a fixed-size persisted enum whose numeric values intentionally differ from `TransactionPriority`. Base `Event` carries `type`, `startTs`, optional `dcId`, and a legacy empty tenant field retained for old data. Concrete event records include `EventGetVersion`, `EventGetVersion_V2`, `EventGetVersion_V3`, `EventGet`, `EventGetRange`, `EventCommit`, `EventCommit_V2`, `EventGetError`, `EventGetRangeError`, and `EventCommitError`. `logEvent()` methods emit `TraceEvent` rows with transaction id, latency, key/range/mutation details, errors, priority, read version, or commit version.

Control flow: Producers construct the versioned event matching the current persisted schema, serialize it into client log data, and later replay/deserializers recover only subclass-local fields on deserialization because the base event header is already consumed by type dispatch. Commit events iterate read conflict ranges, write conflict ranges, and mutations before emitting a summary trace.

State and persistence behavior: Serialized layout is compatibility-sensitive. Versioned structs add fields without mutating old versions: get-version V2 adds priority, V3 adds read version, commit V2 adds commit version. Commit events serialize only `CommitTransactionRequest::transaction` and `arena`, not the full request state. The legacy tenant field remains in the base event for old metadata.

Dependencies and integration points: Depends on `FDBTypes.h` for keys, versions, priorities, and arenas, and `CommitProxyInterface.h` for `CommitTransactionRequest`. Trace emission integrates with Flow `TraceEvent` and transaction tracing analyzers; `TransactionPriorityType` has a static size assertion for external analyzer assumptions.

Risks: Reordering fields, removing legacy tenant state, changing enum values, or serializing different `CommitTransactionRequest` members would break old persisted event records. Trace logging full keys, ranges, and mutations can produce large events, so `setMaxFieldLength()`/`setMaxEventLength()` behavior matters for observability safety. Priority conversion must preserve the intentional enum mismatch.

Test signals: Upgrade simulation that reads old client event records; serialization round trips for each event version; transaction tracing tests for get/getRange/commit/error events; analyzer tests that assume the priority field size; large-key and large-mutation trace truncation checks.
