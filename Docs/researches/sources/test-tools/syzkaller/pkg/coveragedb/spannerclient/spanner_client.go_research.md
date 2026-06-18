# sources/test-tools/syzkaller/pkg/coveragedb/spannerclient/spanner_client.go

Purpose: defines small interfaces over Cloud Spanner and adapts the real Spanner client into those interfaces for testability.

Important APIs/types/functions: interfaces `SpannerClient`, `ReadOnlyTransaction`, `RowIterator`, `Row`; proxy types `SpannerClientProxy`, `SpannerReadOnlyTransactionProxy`, `SpannerRowIteratorProxy`; and `NewClient`.

Control flow: proxy methods forward `Close`, `Apply`, `Single`, `Query`, `Next`, and `Stop` to the real Spanner types. `NewClient` constructs a database path under `projects/<projectID>/instances/syzbot/databases/coverage` and returns a proxy.

State and persistence: wraps a real Spanner client, so callers can read/write the coverage DB. The file itself holds only a client pointer.

Dependencies and integration: used throughout `coveragedb` and mocked by generated files. Depends on `cloud.google.com/go/spanner`.

Risks: database instance/name are hard-coded except project ID. `NewClient` returns a proxy even when `spanner.NewClient` returns an error, with the underlying client potentially nil. Interface surface is intentionally small but must be updated when callers need more Spanner behavior.

Test signals: no direct tests; generated mocks and coverage DB tests validate the interface contract.
