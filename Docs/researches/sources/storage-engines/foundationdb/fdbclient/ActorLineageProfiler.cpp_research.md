# sources/storage-engines/foundationdb/fdbclient/ActorLineageProfiler.cpp

## Purpose

`ActorLineageProfiler.cpp` implements actor-lineage sampling and ingestion. It collects lineage-derived samples, encodes them as msgpack, retains a time window in memory, and optionally ships samples to a configured backend such as FluentD.

## Important APIs, Types, and Functions

- `Packer` wraps `msgpack::packer<msgpack::sbuffer>` and adds overloads for `std::any`, scalar types, strings, maps, and vectors.
- `IALPCollectorBase` registers collectors with `SampleCollector`.
- `SampleCollectorT::collect(ActorLineage*)` and `SampleCollectorT::collect()` gather per-lineage and per-wait-state samples.
- `SampleCollection_t::collect` stores samples, trims the in-memory window, and calls the configured ingestor.
- `sample(LineageReference*)` allocates lineage if needed, annotates actor name, and posts collection to the profiler Asio context.
- `ProfilerImpl` owns `boost::asio::io_context`, timer, work guard, background thread, and sampling frequency.
- `ActorLineageProfilerT` exposes `setFrequency` and `context`.
- `ProfilerConfigT::reset` parses ingestor configuration.
- `samplingProfilerUpdateFrequency` and `samplingProfilerUpdateWindow` are global config callbacks.

## Control Flow

When sampling is enabled, `ProfilerImpl::profileHandler` sets `startSampling` and schedules the next timer based on frequency. Instrumented actors call `sample`, which posts collection into the profiler's Asio context to avoid doing sample work inline. Collection walks registered getters by `WaitState`, asks each collector for named values, msgpack-encodes non-empty vectors, appends the sample to `SampleCollection`, trims old entries, and sends it to the ingestor. Config reset validates backend settings and installs either `NoneIngestor` or `FluentDIngestor`.

## State and Persistence Behavior

State is process-local: sampled data is held in a mutex-protected deque for a configurable window and optionally emitted externally. The profiler owns a background thread for its Asio event loop. Msgpack buffers are released from `sbuffer` as raw `(char*, unsigned)` pairs stored in `Sample::data`.

## Dependencies and Integration Points

The file integrates with Flow network time, actor lineage/name lineage, global config callbacks, `FluentDIngestor`, `NoneIngestor`, msgpack, Boost.Asio, and thread synchronization. It is part of the client profiling infrastructure used by profile-related command paths.

## Risks and Edge Cases

The `Packer` visitor silently logs unsupported `std::any` types instead of throwing, which can produce incomplete samples. The lowercase conversion lambdas in config parsing return `tolower` but do not assign it back to the character, so values may remain case-sensitive. `ProfilerImpl` destructor joins the background thread after resetting the work guard; pending handlers must exit cleanly. `SampleCollection_t::collect` assumes at least one sample remains while trimming.

## Test Signals

The visible fdbcli `profile` integration test exercises profile command state, but not low-level lineage packing or ingestor behavior. Useful tests would cover msgpack encoding of supported `std::any` types, unsupported type logging, frequency/window config callbacks, case-insensitive config parsing, and sample window trimming.
