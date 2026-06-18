<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/doc.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/doc.go

Purpose: package-level documentation for the Go FoundationDB binding.

Important content: describes installation requirement for the C client, `APIVersion` selection, opening databases, transaction-based reads/writes, futures, panic-based `MustGet` convenience, retry behavior in `Database.Transact`, goroutine caveats, range streaming modes, and atomic operations.

Control flow explained: basic usage calls `MustAPIVersion`, opens a database, invokes `db.Transact`, performs writes/async reads, and lets `Transact` commit/retry. Panic flow is documented: `MustGet` panics with `fdb.Error`; `Transact` recovers FDB errors for retry/final return and re-panics non-FDB values.

State and persistence: no executable state. It documents that transactions are the persistence boundary and atomic operations transform values at commit.

Dependencies and integration: documents public package semantics used by `fdb.go`, `database.go`, `transaction.go`, `futures.go`, and generated mutation methods.

Risks: documentation must track API version and current atomic operation list; stale examples can mislead users. It warns that returning futures from transaction functions is unsafe because the transaction can be finalized after `Transact` returns.

Test signals: examples in `fdb_test.go` complement these docs. `go test` examples can catch output drift, but much documented behavior requires a running FDB cluster.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/doc.go -->
