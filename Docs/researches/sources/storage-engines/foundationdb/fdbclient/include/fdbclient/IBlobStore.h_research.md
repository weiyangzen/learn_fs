# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/IBlobStore.h

## Purpose
Defines the common asynchronous blob-store client abstraction used by FoundationDB backup, restore, bulk load, and remote object workflows. The header centralizes endpoint configuration, connection pooling, rate/concurrency limits, request retry hooks, credential lookup, object IO, multipart uploads, bucket management, object listing, and blob-store observability.

## Important APIs, Types, And Functions
`BlobKnobs` holds endpoint knobs for TLS, connection/request retries and timeouts, per-operation rate limits, multipart sizes, concurrent request limits, read caching, byte throttles, SDK auth, integrity checks, and global connection pooling. `BlobStoreConnectionPoolKey` and its `std::hash` make reusable connections shareable by host, service, region, and TLS mode. `IBlobStoreEndpoint` is the reference-counted base interface. It exposes object operations (`objectExists`, `objectSize`, `readObject`, `writeEntireFileFromBuffer`, `deleteObject`, `deleteRecursively`), multipart upload operations, streaming/listing APIs, bucket APIs, credential refresh, request signing/header hooks, request normalization, failure simulation, retry extension hooks, and `doRequest`, `connect`, and `returnConnection` for shared HTTP transport behavior.

## Control Flow
Endpoint construction validates host/proxy settings, builds rate limiters and `FlowLock` concurrency gates, chooses a per-endpoint or global connection pool, and optionally starts counter tracing. Higher-level operations call provider-specific virtual methods, while common request execution flows through `doRequest`, which is declared to handle connection acquisition, retry loops, authentication, HTTP response parsing, and success-code handling. Listing can be streamed via `PromiseStream<ListResult>` so large buckets do not require one monolithic response.

## State And Persistence Behavior
Persistent remote state is the object store: buckets, objects, multipart upload state, metadata/checksums, and deleted objects. Local state includes `BlobKnobs`, extra headers, proxy settings, rate controllers, locks, `ConnectionPoolData`, static aggregate `s_stats`, and optional `BlobStats` counters. The global connection pool is process-aware in simulation: pools are keyed first by `NetworkAddress`, and `ReusableConnection` invalidates copied connections created by a different simulated process.

## Dependencies And Integration Points
The header depends on Flow futures, connections, random IDs, rate control, packet queues, HTTP request/response types, JSON parsing for credentials, client knobs, and tracing counters. Implementations integrate with provider-specific S3/GCS code and with `BlobStoreCommon.cpp` for destructors and common request behavior. `tryReadJSONFile` and `extractCredentialFields` connect credential files to provider credential structs.

## Risks And Test Signals
Risks include retry storms from bad knob combinations, connection reuse across simulated processes, stale credential lookup, proxy/global-pool interactions, integrity-check drift between provider implementations, and partial effects in `deleteRecursively`. Test signals should cover URL parsing/normalization, knob alias parsing, global pool separation in simulation, request retry/failure extension hooks, multipart completion, checksum mismatch handling, streamed list recursion, and rate/concurrency limits under load.
