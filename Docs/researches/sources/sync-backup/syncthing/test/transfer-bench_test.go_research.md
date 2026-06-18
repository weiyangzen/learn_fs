# sources/sync-backup/syncthing/test/transfer-bench_test.go

Purpose: integration benchmark tests for Syncthing transfer throughput under the `integration && benchmark` build tags. The file creates either many small files or one very large file in `s1`, starts two local Syncthing instances, waits for synchronization into `s2`, verifies the result, and logs throughput plus per-process usage.

Important APIs/functions: `TestBenchmarkTransferManyFiles`, `TestBenchmarkTransferLargeFile{1,2,4,8,16,32}G`, `TestBenchmarkTransferSameFiles`, `setupAndBenchmarkTransfer`, `benchmarkTransfer`, and `cleanBenchmarkTransfer`. It depends on helper functions from `util.go` such as `generateFiles`, `generateOneFile`, `directoryContents`, `compareDirectoryContents`, `startInstance`, `checkedStop`, `removeAll`, and platform `printUsage`.

Control flow: benchmark setup removes old `s1`, `s2`, and instance indexes, generates input data, starts sender and receiver via `rc.Process`, resumes both, waits first for a receiver `ItemFinished` event, then waits for `rc.InSync("default", sender, receiver)`. It stops both processes before verification so resource usage is available.

State/persistence: mutates test directories `s1`, `s2`, Syncthing homes `h1`, `h2`, and log files through `startInstance`. It deliberately deletes generated state at both start and end.

Dependencies/integration: requires a built `../bin/syncthing`, configured test homes, Syncthing REST/event APIs from `lib/rc`, and the benchmark-only resource-usage implementation selected by OS.

Risks: very large tests allocate sparse/non-sparse files by copying repeated `../LICENSE` content, so disk pressure is the dominant operational risk. `total/1024/1024` is used as a divisor for per-MiB timing and usage; current benchmark sizes avoid zero, but small future benchmarks could divide by zero. Waiting for the first `ItemFinished` assumes at least one item will finish; the same-files benchmark may rely on event behavior despite no transfer.

Test signals: success requires no fatal test errors, in-sync REST state, byte/mode/mtime/hash directory comparison, and logged wall-time/KiB-per-second/resource metrics.
