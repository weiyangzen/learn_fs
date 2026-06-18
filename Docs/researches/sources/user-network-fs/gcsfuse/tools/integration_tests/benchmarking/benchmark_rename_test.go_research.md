<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/benchmarking/benchmark_rename_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/benchmarking/benchmark_rename_test.go

Purpose: Benchmark integration test for gcsfuse rename latency.

Important APIs, types, and functions: `benchmarkRenameTest` provides `SetupB`, `TeardownB`, and `Benchmark_Rename`. Top-level `Benchmark_Rename` iterates flag sets and delegates to `benchmark_setup.RunBenchmarks`. `expectedRenameLatency` is 1900 ms.

Control flow: Setup mounts gcsfuse and creates a test directory. The benchmark creates `aN.txt` files, then renames each to `bN.txt`, timing only `os.Rename` in the benchmark timer and tracking maximum wall-clock iteration.

State and persistence behavior: Creates and renames files in the mounted bucket. Teardown unmounts and saves logs on failure.

Dependencies and integration points: Uses `setup.BuildFlagSets`, benchmark utilities, and test config from `setup_test.go`. Default configs include `--enable-atomic-rename-object=true`.

Risks and test signals: Rename behavior may differ by bucket type, atomic rename support, and client protocol. Threshold failures indicate regressions or infrastructure anomalies; detailed max iteration logging helps diagnose tail latency.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/benchmarking/benchmark_rename_test.go -->
