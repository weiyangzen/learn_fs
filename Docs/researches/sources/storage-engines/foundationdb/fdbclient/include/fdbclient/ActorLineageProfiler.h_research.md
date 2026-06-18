# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ActorLineageProfiler.h

Purpose: declares the sampling profiler infrastructure for actor lineage collection and ingestion.

Important APIs and types: exposes profiler configuration update functions, collector interfaces (`IALPCollectorBase`, `IALPCollector<T>`), `Sample`, `SampleIngestor`, `NoneIngestor`, `FluentDIngestor`, `ProfilerConfigT`, `SampleCollectorT`, `SampleCollection_t`, and singleton aliases. `ActorLineageProfilerT` owns a PIMPL and a Boost ASIO context.

Control flow: collectors are registered with `SampleCollector`, getters produce lineages by `WaitState`, collection builds `Sample`s, and `ProfilerConfig` forwards samples to the configured ingestor. `SampleCollection` keeps a time-windowed deque under mutex and can collect from a current lineage.

State and persistence: runtime state is in singleton-managed config, collector lists, sample windows, and ingestor backend. FluentD ingestion can externalize profiler samples; otherwise state is memory-only.

Dependencies and integration: builds on `AnnotateActor.h`, Flow singleton/reference types, actor lineage, `WaitState`, standard threading primitives, and a PIMPL to avoid heavy Boost ASIO includes.

Risks: singleton global state, mutexes, atomics, and raw `char*` sample payload ownership require careful lifecycle handling. `Sample` destructor frees captured buffers. Backend reset/config errors must avoid disrupting actor execution.

Test signals: no direct tests here; sampling-enabled builds and profiler integration tests are the relevant signals.
