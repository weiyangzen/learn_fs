<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/benchmarking/benchmark_stat_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/benchmarking/benchmark_stat_test.go

Purpose: Benchmark integration test for stat latency on a mounted gcsfuse file.

Important APIs, types, and functions: `benchmarkStatTest` implements benchmark setup/teardown and `Benchmark_Stat`. Helper `createFilesToStat` creates `benchmarking/a.txt`. `expectedStatLatency` is 1100 ms.

Control flow: The benchmark creates one file, then repeatedly calls `operations.StatFile` on it. Only the stat call is measured by the benchmark timer; max wall-clock latency is tracked separately. Average above threshold is reported as benchmark error.

State and persistence behavior: Creates one test object and repeatedly reads metadata through the mount. Teardown unmounts and preserves logs on failure.

Dependencies and integration points: Depends on integration test operations helpers, benchmark runner, and default configs that disable stat cache (`--stat-cache-ttl=0`) to measure backend/stat path behavior.

Risks and test signals: Threshold is sensitive to network and bucket state. Because stat cache is disabled in defaults, this is more backend/metadata path signal than cache-hit signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/benchmarking/benchmark_stat_test.go -->
