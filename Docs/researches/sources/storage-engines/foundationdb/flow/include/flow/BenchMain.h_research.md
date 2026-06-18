# sources/storage-engines/foundationdb/flow/include/flow/BenchMain.h

Purpose: shared benchmark executable harness that initializes Flow, runs Google Benchmark on a separate thread, and stops the network cleanly.

Important APIs/types/functions: `stopNetworkAfter(Future<Void>)` and `runBenchmarks(int,char**, std::function<void()>)`.

Control flow: initializes Google Benchmark and rejects unknown args, calls `platformInit`, `Error::init`, creates `g_network = newNet2(TLSConfig())`, runs optional extra init, starts a benchmark thread, signals completion back to the main Flow thread with `onMainThreadVoid`, awaits `benchmarksDone`, stops `g_network`, runs the network event loop, joins the thread, and returns.

State/persistence: assigns the global `g_network`; local promise coordinates thread completion.

Dependencies/integration: Google Benchmark, Flow platform/errors/network/TLS/thread helper. Used by `BenchMain.cpp`.

Risks: benchmark functions that require Flow main-thread work rely on this dual-thread/event-loop structure. Exceptions in `stopNetworkAfter` still stop the network and rethrow.

Test signals: running `flow_bench --benchmark_filter=...` successfully starts and stops net2.
