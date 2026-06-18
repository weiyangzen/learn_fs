# sources/storage-engines/foundationdb/fdbclient/bench/BenchPopulate.cpp

Purpose: measures construction/population cost of `Standalone<VectorRef<MutationRef>>` using `emplace_back_deep` versus `push_back_deep`.

Important APIs and control flow: templated `bench_populate<emplace>` creates a fresh standalone vector each iteration, reserves requested item capacity, and appends repeated `SetValue` mutations using either direct emplacement or construction plus push. `getKV` supplies stable key/value buffers.

State and persistence: all state is in-memory arena-backed benchmark data. No database or file persistence.

Dependencies and integration: relies on `CommitTransaction.h`, `FDBTypes.h`, `GlobalData.h`, Flow arena/allocator code, and Google Benchmark. Built into `fdbclient_bench`.

Risks: repeated identical key/value references isolate vector append mechanics rather than realistic transaction mutation diversity. Fresh allocation per benchmark iteration includes arena allocation cost by design.

Test signals: registered ranges cover 1 to 1,048,576 mutations and 1 to 512 byte payload sizes with aggregate-only reporting.
