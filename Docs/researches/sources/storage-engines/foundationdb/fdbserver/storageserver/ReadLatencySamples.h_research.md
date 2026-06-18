# sources/storage-engines/foundationdb/fdbserver/storageserver/ReadLatencySamples.h

Purpose: declares the storage-server read latency sampler.

Important APIs and types: `ReadLatencySamples::SampleType` enumerates ten latency dimensions plus `END`. Private `Entry` owns a fixed array of `LatencySample` pointers. The class stores an aggregate entry and a `ReadType::MAX + 1` array of per-type entries. Public API is `ReadLatencySamples(UID serverId)` and `sample(double latency, SampleType, Optional<ReadType>)`.

Control flow, state, and persistence: in-memory metric sample holders only. Sampling produces trace/metric output through `LatencySample`.

Dependencies and integration: includes FDB type definitions and stats. Storage-server read code can include this header without depending on construction details.

Risks and test signals: risks are array bounds if new sample/read types are added without matching constructors, and optional read type misuse. Tests should instantiate the sampler, sample every enum value, and verify no crash with absent read type.
