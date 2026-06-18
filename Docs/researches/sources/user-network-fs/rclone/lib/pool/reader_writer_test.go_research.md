# sources/user-network-fs/rclone/lib/pool/reader_writer_test.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/pool/reader_writer_test.go -->
## sources/user-network-fs/rclone/lib/pool/reader_writer_test.go

Purpose: validates the `RW` pool-backed reader/writer across simple operation, accounting, page boundaries, and concurrent producer/consumer usage.

Important APIs and control flow: `TestRW` builds small buffers with `ReadFrom`, checks EOF behavior, `Seek`, `Read`, `WriteTo`, writer error propagation, accounting callbacks, delayed accounting after N passes, and accounting-error propagation. `TestRWBoundaryConditions` iterates sizes and chunk sizes around page boundaries, combining `Write` or `ReadFrom` with `Read` or `WriteTo` to assert exact byte preservation and accounting totals. `TestRWConcurrency` starts writer and reader goroutines and uses `WaitWrite` to read as data arrives from pattern readers.

State, dependencies, and integration: the test uses a package-level `rwPool`, custom chunking reader/writer types, `readers.NewPatternReader`, random test data, and `sync.WaitGroup`. It checks `RW.Size`, returned byte counts, EOFs, and accounting side effects.

Risks and test signals: the tests give strong coverage for page-boundary correctness and the intended one-reader/one-writer concurrency model. They do not explicitly test `Reserve`, close-after-close behavior, multiple simultaneous readers, or races beyond normal `go test` unless run with `-race`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/pool/reader_writer_test.go -->
