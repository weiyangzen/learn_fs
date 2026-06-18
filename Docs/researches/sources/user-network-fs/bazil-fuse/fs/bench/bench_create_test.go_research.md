<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/bench/bench_create_test.go -->
# sources/user-network-fs/bazil-fuse/fs/bench/bench_create_test.go

Purpose: benchmark FUSE create throughput with a subprocess performing many `os.Create` calls against a minimal filesystem.

Important APIs, types, and functions: `benchCreateDir.Create` returns a dummy file as both node and handle; `benchCreateHelp` exposes `/init` and `/bench` through `httpjson.ServePOST`; `BenchmarkCreate` mounts with `fstestutil.MountedT`.

Control flow: benchmark prepares deterministic filenames in the helper, resets the timer, then asks the helper subprocess to create `b.N` files under the FUSE mount.

State and persistence behavior: helper stores filename list under mutex; scratch mount contents are temporary.

Dependencies and integration points: uses fstestutil mounting, spawntest helper subprocesses, HTTP JSON control, and Go benchmark framework.

Risks and test signals: helper uses `log.Fatalf`, killing the subprocess on errors. Benchmark signal is create operations per second with reduced in-process overhead.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/bench/bench_create_test.go -->
