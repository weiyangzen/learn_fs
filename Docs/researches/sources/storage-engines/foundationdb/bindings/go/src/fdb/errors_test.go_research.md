<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/errors_test.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/errors_test.go

Purpose: tests Go error wrapping and sentinel matching semantics for `fdb.Error`.

Important tests: `TestErrorWrapping` selects API version 800, opens the default database, and passes nil, value/pointer FDB errors, wrapped FDB errors, and a custom error through `db.ReadTransact`, expecting the same error object/value to be returned. `TestErrorIs` verifies `errors.Is` against `ErrTransactionTooOld`, pointer targets, wrapped value/pointer errors, wrong codes, and unrelated errors.

Control flow: `ReadTransact` is used to confirm retryable machinery does not unwrap or replace non-retry path errors returned by the user function. `errors.Is` targets the `Error.Is` implementation directly.

State and persistence: requires a selected API version and a default database for `TestErrorWrapping`, but does not intentionally mutate data.

Dependencies and integration: depends on `fdb.go` API selection/opening, `database.go` read transaction behavior, generated `ErrTransactionTooOld`, and Go standard `errors`.

Risks: `TestErrorWrapping` requires an accessible FDB cluster/default cluster file, so it is integration-like and can fail in minimal environments. It compares interface error values directly; wrapping cases are stable because returned input should be identical, not merely equivalent.

Test signals: strong coverage for the new `errors.Is` contract; limited coverage across only one code value.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/errors_test.go -->
