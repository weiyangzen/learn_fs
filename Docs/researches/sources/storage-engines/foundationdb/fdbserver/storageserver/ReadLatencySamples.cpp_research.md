# sources/storage-engines/foundationdb/fdbserver/storageserver/ReadLatencySamples.cpp

Purpose: implements storage-server read latency metric sampling by constructing aggregate and per-read-type latency sketches.

Important APIs and functions: private `createSample` builds a `LatencySample` named from a prefix and metric name using server id, logging interval, sketch accuracy, and silent-interval suppression. `ReadLatencySamples::Entry` creates samples for read, getKey, getValue, getRange, read-version wait, queue wait, KV getRange, mapped range, remote mapped range, and local mapped range. `ReadLatencySamples::sample` records into aggregate and optional per-type samples.

Control flow, state, and persistence: state is owned `LatencySample` objects that emit metrics through tracing infrastructure. No durable storage is used.

Dependencies and integration: depends on storage server knobs and `LatencySample`. Called by storage read paths to report latency dimensions for aggregate and eager/fetch/priority read categories.

Risks and test signals: risks are enum index mismatch between `SampleType` and arrays, missing per-type sample when `ReadType` exceeds `MAX`, and metric-name drift. Signals are expected TraceEvent latency metric names and non-overlapping aggregate/per-type counts.
