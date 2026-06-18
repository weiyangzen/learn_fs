# sources/test-tools/syzkaller/pkg/coveragedb/mocks/ReadOnlyTransaction.go

Purpose: generated testify mock for the `spannerclient.ReadOnlyTransaction` interface.

Important APIs/types/functions: `NewReadOnlyTransaction`, `ReadOnlyTransaction`, `ReadOnlyTransaction_Expecter`, `EXPECT`, `Query`, and typed call helper `ReadOnlyTransaction_Query_Call`.

Control flow: constructor registers test cleanup to assert expectations. `Query` delegates to `mock.Called(ctx, statement)`, panics if no return value is specified, and type-asserts a `spannerclient.RowIterator`. Helper methods support `Run`, `Return`, and `RunAndReturn`.

State and persistence: stores mock call expectations in memory; no database access.

Dependencies and integration: used by `coveragedb_test.go` to mock `client.Single().Query(...)`. Depends on `cloud.google.com/go/spanner`, `spannerclient`, and testify mock.

Risks: generated code should not be manually edited. Type assertions panic if tests return the wrong type. Expectations assert exact calls unless matchers are used.

Test signals: this file is test infrastructure; its correctness is exercised whenever coverage DB tests use read-only query mocks.
