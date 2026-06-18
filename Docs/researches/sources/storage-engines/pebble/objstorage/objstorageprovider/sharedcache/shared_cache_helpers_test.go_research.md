# sources/storage-engines/pebble/objstorage/objstorageprovider/sharedcache/shared_cache_helpers_test.go

Purpose: This test helper exposes a synchronization hook for the shared cache's asynchronous write-back workers.

Important API: `(*Cache).WaitForWritesToComplete` closes the current worker task channel, waits for all worker goroutines to exit, then restarts the same number of workers.

Control flow and state: Tests call this after a read miss to force queued cache writes to complete before issuing a second read that should hit. The helper reaches into unexported `writeWorkers` state because it is compiled in the same package for tests.

Dependencies and integration: It is used by `shared_cache_test.go` data-driven cache tests. It depends on `writeWorkers.tasksCh`, `doneWaitGroup`, `Start`, and `numWorkers`.

Risks and test signals: This is a test-only lifecycle manipulation. It would be unsafe as a production API because closing the queue while callers may concurrently enqueue writes would panic or race. In the controlled tests, it provides deterministic cache-hit expectations after asynchronous fills.
