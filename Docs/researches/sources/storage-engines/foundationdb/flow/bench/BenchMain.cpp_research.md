# sources/storage-engines/foundationdb/flow/bench/BenchMain.cpp

Purpose: provides the executable entry point for `flow_bench`.

Important APIs/types/functions: `main(int argc, char** argv)` delegates directly to `runBenchmarks` from `flow/BenchMain.h`.

Control flow: all initialization, network setup, benchmark thread handling, and shutdown semantics live in the included harness; this file is intentionally minimal.

State/persistence: no local state beyond command-line arguments.

Dependencies/integration: depends only on `flow/BenchMain.h`, tying the binary target built by the bench CMake file to the shared benchmark harness.

Risks: any extra initialization must be added through `runBenchmarks` or an alternate entry point; this file provides no error handling beyond the harness return code.

Test signals: executable behavior is validated indirectly by running any registered Google Benchmark from the `flow_bench` target.
