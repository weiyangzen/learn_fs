## sources/user-network-fs/gcsfuse/internal/gcsx/integration_test.go

Purpose: integration-style test suite for higher-level gcsx object mutation, read, sync, append, truncate, and conflict behavior against a bucket-backed test setup.

Important APIs and fixtures: `IntegrationTest`, `SetUp`, `TearDown`, `create`, `objectGeneration`, `sync`, `randBytes`, and registered jacobsa test suite methods such as `ReadThenSync`, `SyncEmptyLocalFile`, `WriteThenSync`, `AppendThenSync`, `TruncateThenSync`, and conflict tests.

Control flow and behavior covered: tests create objects, instantiate local object state, read existing contents, write local content, sync to GCS, verify object generations and contents, and list temporary-object prefixes to ensure no stale temp objects remain. Dirty stat behavior checks size, dirty threshold, and mtime tracking. Conflict tests delete or overwrite backing objects and expect precondition/not-found behavior during sync/read.

State/persistence signals: directly exercises persistent GCS object generations, object contents, local dirty thresholds, local mtime metadata, and remote cleanup of temporary append compose objects. Multiple-interaction scenarios mix reads/writes/truncates/syncs and compare resulting remote content.

Dependencies/integration: depends on the project’s integration harness, bucket fixture, gcs object APIs, local object abstractions outside this file, and `timeutil` matchers.

Risks/test signals: strong end-to-end signal for gcsx semantics, especially generation preconditions and temp cleanup. It may require integration credentials or a fake integration environment and is slower/flakier than pure unit tests.
