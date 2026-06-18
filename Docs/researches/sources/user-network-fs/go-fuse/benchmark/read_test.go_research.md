# sources/user-network-fs/go-fuse/benchmark/read_test.go

Purpose: benchmarks read throughput for synthetic go-fuse memory reads, loopback FD reads, and optional libfuse passthrough.

Important functions: `BenchmarkGoFuseMemoryRead` mounts `readFS` and runs `benchmarkRead` with `dd iflag=direct`; `benchmarkRead` launches one `dd` process per `GOMAXPROCS`, sets benchmark bytes to readers times block size, captures output unless verbose, and reports subprocess failures; `BenchmarkGoFuseFDRead` writes a backing file and mounts loopback; `BenchmarkLibfuseHP` starts an external libfuse passthrough binary when `--passthrough_hp` is supplied.

Dependencies/integration: uses `dd`, `fusermount`, optional libfuse helper, temp dirs, and `setupFS` from `stat_test.go`.

Risks/test signals: external process failures are surfaced with buffered output. Large `b.N` can create large backing files. The benchmarks exercise direct I/O, loopback file handles, and subprocess interaction with mounted FUSE filesystems.
