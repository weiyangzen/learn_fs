<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/multiclient_test/framework/filewriter.go -->
# sources/sync-backup/kopia/tests/robustness/multiclient_test/framework/filewriter.go

This file multiplexes `robustness.FileWriter` instances by multiclient context. `MultiClientFileWriter` owns a map from client ID to concrete file writer, guarded by an `RWMutex`, and a factory `newFileWriterFn`.

The wrapper methods implement the `FileWriter` interface by calling `createOrGetFileWriter` and delegating `DataDirectory`, write, delete, and cleanup operations. If a context lacks a client, it logs and returns `robustness.ErrKeyNotFound`. Cleanup iterates all client writers, calls their cleanup hooks, and removes map entries.

State persists only for the test process lifetime: one FIO data root per client. Integration points are the multiclient harness and FIO writer. Risks include lazy-creation races: lookup happens under `RLock`, creation happens outside the write lock, so concurrent first use of the same client can duplicate work before the final map write. Tests cover behavior indirectly through concurrent multiclient robustness tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/multiclient_test/framework/filewriter.go -->
