# sources/storage-engines/foundationdb/flow/include/flow/IConnection.h

## Purpose
`IConnection.h` defines TCP connection/listener abstractions, DNS cache support, and the `INetworkConnections` interface for connecting, listening, UDP creation, and endpoint resolution.

## Important APIs, Types, And Functions
Key types are `IConnection`, `IListener`, `DNSCache`, and `INetworkConnections`. APIs cover handshakes, readability/writability futures, `read()`, `write(SendBuffer)`, peer/trust/debug/socket access, listener `accept()`, DNS cache add/update/remove/parse/stringify, connect/listen/resolve variants, and `pickOneAddress()`.

## Control Flow
Callers create outgoing connections through `INetworkConnections::connect*()` or accept through `IListener::accept()`. Nonblocking I/O alternates immediate `read()`/`write()` calls with `onReadable()`/`onWritable()` waits. Host/service connect resolves addresses and selects one, preferring IPv6 unless a knob requests IPv4.

## State And Persistence Behavior
Connections are reference counted but must be explicitly closed. DNS cache stores host/service entries with addresses and last-access timestamps. Connection state and send buffers live in backend implementations.

## Dependencies And Integration Points
It depends on Boost.Asio TCP sockets, `Knobs`, `NetworkAddress`, `network.h`, `IRandom`, `FLOW_KNOBS`, and `g_network` global slots. TLS wrappers override external hostname/SNI and trust behavior.

## Risks And Edge Cases
`write()` has a strong commitment contract: callers must continue writing the same byte prefix if partially written, and TLS limitations restrict first-buffer shrinkage. Incoming peer addresses may not be reconnectable. DNS cache staleness and IPv4/IPv6 preference affect availability.

## Test Signals
Tests should cover partial reads/writes, readiness futures, close/cancel, TLS trust/SNI, listener accept, DNS cache parse/update/access time, address selection knobs, blocking vs async resolve, and socket backend error propagation.
