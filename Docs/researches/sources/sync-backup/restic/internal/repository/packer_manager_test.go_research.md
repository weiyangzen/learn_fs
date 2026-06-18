
# sources/sync-backup/restic/internal/repository/packer_manager_test.go

Purpose: tests and benchmarks the packer manager's pack filling, flush, and accounting behavior.

`fillPacks` writes 102 random data blobs up to 1 MiB into a manager and validates `SaveBlob` byte accounting against blob length plus header-entry overhead, with optional final pack header overhead. `TestPackerManager` records total size once for benchmark reuse. `TestPackerManagerWithOversizeBlob` exercises the dedicated-packer path for blobs at or above the pack size. `BenchmarkPackerManager` measures repeated pack creation and flushing.

The tests use a `queueFn` that finalizes packers and accumulates size instead of saving to a backend. State coverage focuses on open packers, flush behavior, and pack sizes. Risks covered include invalid byte accounting, packer exhaustion, oversize blob treatment, and merge/flush output size mismatches.
