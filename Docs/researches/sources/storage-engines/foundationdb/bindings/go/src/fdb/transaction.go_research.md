<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/transaction.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/transaction.go

Purpose: implements transaction and read transaction APIs over the FoundationDB C transaction pointer.

Important APIs: `ReadTransaction`, `Transaction`, `transaction`, `TransactionOptions`, `Transact`, `ReadTransact`, `Cancel`, `SetReadVersion`, `Snapshot`, `OnError`, `Commit`, `Watch`, `Get`, `GetRange`, `GetEstimatedRangeSizeBytes`, `GetRangeSplitPoints`, `GetReadVersion`, `Set`, `Clear`, `ClearRange`, `GetCommittedVersion`, `GetVersionstamp`, `GetApproximateSize`, `Reset`, `GetKey`, conflict range/key methods, `Options`, and `LocalityGetAddressesForKey`.

Control flow: read methods allocate typed futures around C calls; writes and atomic operations mutate the transaction immediately client-side; commit returns a future. `Transact`/`ReadTransact` on an existing transaction provide composition and panic recovery but no retry/commit. Range reads translate `Range` selectors and `RangeOptions` into C arguments.

State and persistence: `transaction` owns `*C.FDBTransaction` and parent `Database`. Mutations persist only after successful `Commit`. Conflict ranges alter commit conflict behavior. Watches outlive the transaction after commit and must be canceled if unused.

Dependencies and integration: central consumer of futures, key selectors, range abstractions, generated options/mutations, and database retry logic.

Risks: using a transaction after commit/reset/cancel can fail; concurrent `Reset`/`Cancel` is documented unsafe. `AddReadConflictKey` uses key plus `0x00`, which is not the same as `Strinc` for all logical keyspaces but matches single-key conflict convention. Returning futures outside retry functions is unsafe. C pointer lifetime depends on finalization in database code.

Test signals: `fdb_test.go` exercises read options, versionstamps, range iteration, estimated range size, and transactor composition.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/transaction.go -->
