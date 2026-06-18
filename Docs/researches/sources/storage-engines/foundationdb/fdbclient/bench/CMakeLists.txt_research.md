# sources/storage-engines/foundationdb/fdbclient/bench/CMakeLists.txt

Purpose: builds the fdbclient Google Benchmark executable.

Important APIs and control flow: includes `FDBBenchmark`, discovers benchmark sources with `fdb_find_sources(FDBCLIENT_BENCH_SRCS)`, creates `fdbclient_bench` via `add_flow_target`, initializes Google Benchmark with `fdb_setup_googlebenchmark`, adds the current source directory to private includes, and links `Threads::Threads`, `fdb_google_benchmark`, and `fdbclient`.

State and persistence: no runtime state; it contributes build graph metadata.

Dependencies and integration: depends on FoundationDB's CMake helper macros and the fdbclient library. The private include path lets benchmark sources include `GlobalData.h` as a local header.

Risks: source discovery can unintentionally include newly added benchmark files. Link dependencies must provide Flow runtime, benchmark main support, and fdbclient symbols.

Test signals: successful CMake configuration and build of `fdbclient_bench`; execution validates benchmark registration.
