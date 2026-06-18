# sources/user-network-fs/go-fuse/benchmark/readfs.go

Purpose: implements a synthetic filesystem for raw read-throughput benchmarking.

Important APIs/types: `readFS` embeds `fs.Inode` and implements `NodeLookuper`, `NodeGetattrer`, `NodeOpener`, and `fs.FileReader`. Any lookup returns a regular-file inode. `Getattr` reports a huge `fileSize` (`2 << 60`) and one-hour attr timeout. `Open` returns a `readFS` file handle with `FOPEN_DIRECT_IO`; `Read` returns the incoming destination buffer as zero-filled data.

Control flow/state: stateless and allocation-minimal. There is no backing storage; reads are synthesized.

Dependencies/integration: used by `BenchmarkGoFuseMemoryRead`. Risks include unrealistic semantics compared with real files, and every name resolves successfully, but that is intentional for throughput isolation. Test signal comes through `dd` benchmark success.
