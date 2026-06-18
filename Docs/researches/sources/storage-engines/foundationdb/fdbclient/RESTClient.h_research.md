# sources/storage-engines/foundationdb/fdbclient/RESTClient.h

## Purpose
`RESTClient.h` declares the `RESTClient` interface for sending common HTTP REST verbs to a URL-backed resource with connection pooling, knobs, and statistics.

## Important APIs, Types, and Functions
- `RESTClient::Stats` is the externally visible stats record for one `host:service`.
- `RESTClientKnobs knobs` stores connection and request retry/timeout settings.
- `Reference<RESTConnectionPool> conectionPool` owns reusable network connections. The member name is misspelled as `conectionPool` and consumers must use that spelling.
- `statsMap` maps `host:service` strings to `Stats`.
- Public methods cover GET, HEAD, DELETE, TRACE, PUT, and POST. PUT/POST accept request bodies.
- `getStatsKey(host, service)` standardizes map keys.
- Private helpers split bodyless verbs and body verbs.

## Control Flow and State
The header defines asynchronous APIs returning `Future<Reference<HTTP::IncomingResponse>>`. Callers pass optional headers; methods parse full URLs internally and then dispatch through shared implementation helpers in the `.cpp` file.

## State and Persistence Behavior
All state is in-memory and scoped to the `RESTClient` instance. Stats accumulate until `clear` or object destruction. Connections are held in the pool and reused across requests to the same endpoint.

## Dependencies and Integration Points
The header depends on `JSONDoc`, `fdbrpc/HTTP`, `RESTUtils`, Flow arenas/ref counting, and packet types. It provides a generic REST layer used by code that does not need S3-specific signing or blob-store behavior.

## Risks and Edge Cases
- The public API exposes raw HTTP response objects, so callers must validate response bodies and headers themselves.
- Knob changes after construction update `knobs` but do not resize or rebuild existing connection-pool state immediately.
- The private helper split makes it easy for verb dispatch bugs to affect multiple public methods.

## Test Signals
Tests should instantiate default and override knob configurations, validate per-verb status-code acceptance, check optional header propagation, and verify stats JSON/delta behavior.
