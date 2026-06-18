<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/fdb_test.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/fdb_test.go

Purpose: examples and integration tests for the public Go `fdb` package.

Important tests/examples: `ExampleOpenDefault`, `TestVersionstamp`, `TestEstimatedRangeSize`, `TestReadTransactionOptions`, `ExampleTransactor`, `ExampleReadTransactor`, `ExamplePrefixRange`, `ExampleRangeIterator`, `TestKeyToString`, `ExamplePrintable`, `TestDatabaseCloseRemovesResources`, `ExampleOpenWithConnectionString`, skipped `TestGetClientStatus`, and `ExampleDatabase_GetClientStatus`.

Control flow: tests select API version 800, open default databases, demonstrate composable transactors/read transactors, create transactions, perform uncommitted example mutations/range scans, fetch versionstamp futures, read system keys with options, and verify database close removes cached handles.

State and persistence: examples intentionally avoid commits for data mutation examples. Some tests require a live FDB cluster and default or env-specified cluster configuration. `TestVersionstamp` does commit via `Transact` and writes `foo`.

Dependencies and integration: exercises `fdb.go`, `database.go`, `transaction.go`, `range.go`, `subspace`, generated options, futures, and C client integration.

Risks: tests are environment-sensitive and can mutate default database (`foo`) unless isolated. API version selection is global, so tests assume consistent version. Examples using uncommitted transactions rely on read-your-writes semantics.

Test signals: covers public examples, key formatting, close/cache semantics, versionstamp and range behavior; multi-version client status test is explicitly skipped.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/fdb_test.go -->
