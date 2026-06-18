<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/benchmarking/benchmark_delete_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/benchmarking/benchmark_delete_test.go

Purpose: Benchmark integration test that measures average gcsfuse file deletion latency and fails when it exceeds an expected threshold.

Important APIs, types, and functions: `benchmarkDeleteTest` implements `SetupB`, `TeardownB`, and `Benchmark_Delete`. Top-level `Benchmark_Delete` builds compatible flag sets and runs the benchmark via `benchmark_setup.RunBenchmarks`. `expectedDeleteLatency` is 1800 ms.

Control flow: Setup mounts gcsfuse and creates a test directory. The benchmark precreates `b.N` files, resets/stops the timer, and for each iteration times only `os.Remove` with the benchmark timer while also tracking wall-clock max latency. Average latency is `b.Elapsed()/b.N`; exceeding the threshold reports errors.

State and persistence behavior: Creates and deletes objects through the mounted filesystem. Teardown unmounts gcsfuse and saves logs on failure.

Dependencies and integration points: Depends on benchmark setup utilities, configured test bucket/mount, gcsfuse flags built from config, and Go benchmark runner semantics. It is skipped for presubmit via `setup.IgnoreTestIfPresubmitFlagIsSet`.

Risks and test signals: Threshold is environment-sensitive and set as anomaly detection rather than precise performance target. Precreating `b.N` files can be expensive for high benchtime. Provides direct signal on delete performance for flat/HNS/zonal-compatible configs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/benchmarking/benchmark_delete_test.go -->
