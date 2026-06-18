# sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/read_only_test.go

Purpose: Covers read-only file-cache behavior for repeated sequential reads, oversized files, random reads, and cache capacity across multiple files.

Important APIs/types/functions: `readOnlyTest` uses the common suite. Helpers `readMultipleFiles` and `validateCacheOfMultipleObjectsUsingStructuredLogs` batch reads and log validation. Tests call `readFileAndValidateCacheWithGCS`, `readFileAndValidateFileIsNotCached`, `client.CreateNFilesInDir`, and structured read-log validation.

Control flow: second-read test expects miss then hit for a cacheable file. Oversized sequential and random tests use a file larger than cache capacity and expect no cached file and repeated misses. Multi-file tests create enough 3 MiB files to fit within or exceed the 9 MiB cache capacity, read all files twice, and validate second-pass hit/miss behavior based on capacity.

State/persistence: Cache contents are directly tied to configured 9 MiB capacity. Files are created in a unique test directory via storage client and read through the mount.

Dependencies/integration: Uses read-cache helpers, setup/client/operations, structured logs, and suite runner.

Risks/test signals: Tests assume LRU/capacity behavior is deterministic across sequential reads. Passing signals cache admission and eviction policy for common read-only workloads.
