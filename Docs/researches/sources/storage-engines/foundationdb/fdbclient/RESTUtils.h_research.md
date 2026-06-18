# sources/storage-engines/foundationdb/fdbclient/RESTUtils.h

## Purpose
`RESTUtils.h` declares the utility types that make the REST client work: connection-pool keys, reusable connections, supported protocols, REST knobs, parsed URLs, and a decay helper.

## Important APIs, Types, and Functions
- `RESTConnectionPoolKey` is `(host, service)`.
- `RESTLogSeverity` defines `INFO`, `DEBUG`, and `VERBOSE` levels checked against Flow REST logging knobs.
- `RESTConnectionPool::ReusableConnection` bundles `Reference<IConnection>` with an expiration time.
- `RESTConnectionPool` owns `connectionPoolMap`, connects, returns connections, and builds keys with `getConnectionPoolKey`.
- `RESTConnectionType` stores protocol plus secure flag and exposes supported protocol queries.
- `RESTClientKnobs` stores pool, connect, and request retry/timeout values, with `set`, `get`, and descriptions.
- `RESTUrl` exposes parsed `host`, `service`, `resource`, `reqParameters`, `body`, and `connType`.

## Control Flow and State
The declarations establish an explicit checkout/return connection lifecycle. `RESTUrl` construction immediately parses and validates a full URL. `RESTClientKnobs` is mutable, letting clients adjust request behavior at runtime.

## State and Persistence Behavior
All state is local to objects using this header. `connectionPoolMap` queues reusable connections by endpoint. `RESTUrl` stores a copy of parsed URL data and request body.

## Dependencies and Integration Points
The header depends on Flow futures/ref counting/packet types, boost pair hashing for unordered map keys, and fmt formatting. It is included by both REST client implementation and likely any code constructing REST URLs or knobs.

## Risks and Edge Cases
- `max_connection_life` is documented as not fully implemented in `RESTClientKnobs`, although the pool uses a max-life value when creating expiration timestamps.
- `RESTUrl::toString` includes the request body, so verbose trace logging can expose payload data.
- `RESTConnectionType::secure` is an `int` rather than bool, reflecting existing serialization/logging conventions but requiring care in boolean contexts.

## Test Signals
Header-level behavior is covered through `RESTUtils.cpp` and `RESTClient.cpp` tests. Compile-time tests should ensure connection pool keys hash correctly and knob descriptions stay in sync with accepted knob names.
