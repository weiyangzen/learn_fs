# sources/storage-engines/foundationdb/fdbclient/RESTUtils.cpp

## Purpose
`RESTUtils.cpp` implements REST connection pooling, supported protocol handling, REST client knob mapping, URL parsing, and a small continuous-time decay utility.

## Important APIs, Types, and Functions
- `RESTConnectionPool::~RESTConnectionPool` explicitly closes pooled connections in simulation.
- `RESTConnectionType::supportedConnTypes`, `getConnectionType`, `isProtocolSupported`, and `isSecure` support `http` and `https`.
- `RESTClientKnobs` initializes from Flow knobs and maps full names plus aliases such as `pz`, `ct`, `cto`, `mcl`, `rt`, and `rtom`.
- `connect_impl` reuses unexpired connections or creates a new connection with `INetworkConnections::net()->connect` and `connectHandshake`.
- `RESTConnectionPool::returnConnection` returns non-expired connections up to the per-key capacity.
- `RESTUrl::parseUrl` splits protocol, host, optional service, resource path, and query parameters.
- `continuousTimeDecay` computes `initialValue * exp(-decayRate * time)`.

## Control Flow and State
Connection acquisition first checks the queue for a matching `(host, service)` key, discarding expired entries. If no reusable connection exists, it connects and records an expiration timestamp. Return logic pushes the connection back only if it remains unexpired and the queue is under capacity.

URL parsing uses `StringRef::eat` and `eatAny` to parse `<protocol>://<host>[:service][/resource][?params]`, defaulting the resource to `/`. Unsupported protocols and empty hosts become FoundationDB REST errors.

## State and Persistence Behavior
The connection pool is in-memory and keyed by host/service. Expiration is wall-clock/runtime state based on `now()`. Knobs are copied into the `RESTClientKnobs` object and are not persisted.

## Dependencies and Integration Points
The file integrates Flow networking, `IConnection`, Flow knobs, tracing, boost string utilities, and Flow unit tests. It is the utility backend for `RESTClient.cpp`.

## Risks and Edge Cases
- `RESTClientKnobs::set` asserts that the input key equals the stored map key. Alias keys satisfy this because the map key is the alias, but any future normalization must preserve that invariant.
- URL parsing is intentionally simple and does not fully implement RFC URL syntax, userinfo, IPv6 literals, or percent-decoding.
- Service can be empty, which depends on lower networking layers to choose defaults or fail clearly.
- Expired connections are popped but not explicitly closed outside the simulation destructor path.

## Test Signals
The file includes unit tests for invalid protocol, missing host, valid URI with/without service, extra slash paths, and query parameters. Additional coverage should check HTTP protocol security false, aliases in `RESTClientKnobs`, connection reuse capacity, expiration, and empty service handling.
