# sources/sync-backup/kopia/repo/blob/logging/logging_storage_test.go

Purpose: tests the logging storage wrapper against a real underlying storage.

Important APIs/types/functions: `TestLoggingStorage`, `logging.NewWrapper`, generic blob operations, and test logging/content-log setup.

Control flow: the test wraps a base storage, performs representative blob operations, and verifies behavior still matches expected storage semantics while logging paths execute.

State and persistence behavior: blob state is held by the test storage; wrapper adds only logging/concurrency state.

Dependencies/integration points: validates wrapper composition with the blob interface and ensures logging does not break operation results. Risks/test gaps include limited assertions on actual log records, no max-concurrency race test, no OpenTelemetry span inspection, and no `ExtendBlobRetention` coverage. It is primarily a smoke/regression test for delegation.
