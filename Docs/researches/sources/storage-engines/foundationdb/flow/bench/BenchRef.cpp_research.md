# sources/storage-engines/foundationdb/flow/bench/BenchRef.cpp

Purpose: compares allocation, destruction, and copy overhead for raw pointers, `unique_ptr`, `shared_ptr`, Flow `Reference`, and thread-safe Flow `Reference`.

Important APIs/types/functions: empty reference-counted types `Empty` and `EmptyTSRC`; enum `RefType`; specialized `Factory` templates; benchmarks `bench_ref_create_and_destroy` and `bench_ref_copy`.

Control flow: create/destroy benchmarks construct one object per iteration and invoke type-specific cleanup. Copy benchmarks create one pointer-like object before timing and repeatedly copy it.

State/persistence: no persistent state. Allocations are per benchmark iteration for creation tests and one per benchmark state for copy tests.

Dependencies/integration: uses Flow `FastAlloc`, `FastRef`, standard smart pointers, and Google Benchmark.

Risks: raw pointer cleanup is manual and only safe because the benchmark calls `Factory::cleanup`. Copy benchmarks do not include `unique_ptr` because it is noncopyable.

Test signals: registrations cover creation/destruction for all five pointer styles and copy for raw, shared, Flow reference, and thread-safe Flow reference.
