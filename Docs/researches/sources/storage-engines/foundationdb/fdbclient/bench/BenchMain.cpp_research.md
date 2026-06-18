# sources/storage-engines/foundationdb/fdbclient/bench/BenchMain.cpp

Purpose: executable entry point for the fdbclient benchmark binary.

Important APIs and control flow: `main` forwards `argc` and `argv` to `runBenchmarks` from `flow/BenchMain.h`, which owns Google Benchmark initialization and execution.

State and persistence: no local state and no persistence. Runtime state is managed by the benchmark harness.

Dependencies and integration: linked into `fdbclient_bench` by the bench CMake target. It is intentionally minimal so benchmark translation units register their workloads statically.

Risks: failures here would affect all fdbclient benchmarks. The file assumes the Flow benchmark wrapper is linked and initializes any required FoundationDB runtime pieces.

Test signals: successful execution of the benchmark binary validates this entry point; there are no unit tests.
