<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/snapshot.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/snapshot.go

Purpose: exposes snapshot read behavior for an existing transaction.

Important APIs: `Snapshot`, `ReadTransact`, `Cancel`, `Snapshot`, `Get`, `GetKey`, `GetRange`, `GetReadVersion`, `GetDatabase`, `GetEstimatedRangeSizeBytes`, `GetRangeSplitPoints`, and `Options`.

Control flow: `Transaction.Snapshot` wraps the same internal transaction pointer. Snapshot read methods call the transaction helpers with snapshot flag set to 1/true, while size/split/read-version operations reuse non-mutating transaction helpers. `ReadTransact` recovers `Error` panics but does not retry.

State and persistence: no independent state; shares underlying transaction state and lifetime. Snapshot reads reduce conflict creation but still use the transaction's read version and read-your-writes configuration where applicable.

Dependencies and integration: satisfies `ReadTransaction` and `ReadTransactor`; used by composable read-only functions and directory prefix checks.

Risks: canceling a snapshot cancels the underlying transaction. Snapshot isolation is weaker, making invariants harder to reason about. Options returns transaction options, so callers can change the whole transaction via a snapshot handle.

Test signals: `ExampleReadTransactor` uses `rtr.Snapshot()` composition; broader tests should cover conflict behavior and cancellation side effects.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/snapshot.go -->
