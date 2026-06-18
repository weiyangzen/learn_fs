# sources/storage-engines/foundationdb/fdbclient/bench/BenchVersionVectorSerialization.cpp

Purpose: compares generic object serialization against specialized `dynamic_size_traits<VersionVector>` serialization.

Important APIs and control flow: `TestContextArena` supplies arena allocation and protocol version. `bench_serializable_traits_version` serializes via `ObjectWriter::toValue` and reads via `ObjectReader`. `bench_dynamic_size_traits_version` computes size, writes to an arena buffer, and loads directly. Both populate a same-locality vector of `tagCount` tags and assert equality after deserialization.

State and persistence: serialization buffers are in-memory, but represent FoundationDB wire/storage encoding choices for version vectors.

Dependencies and integration: includes Flow arena, Google Benchmark, `VersionVector.h`, `g_network->protocolVersion`, and FDB serialization APIs.

Risks: the arena in the dynamic benchmark is reused across iterations, so allocation accumulation may affect long runs. The benchmark uses simple sequential tags and versions, not the randomized multi-locality cases from unit tests.

Test signals: both benchmark registrations cover 16 to 1024 tags and report item count plus serialized size.
