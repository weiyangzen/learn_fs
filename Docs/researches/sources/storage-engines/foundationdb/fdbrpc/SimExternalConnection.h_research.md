# sources/storage-engines/foundationdb/fdbrpc/SimExternalConnection.h

## Purpose
`SimExternalConnection.h` declares the `SimExternalConnection` concrete `IConnection` used by simulation to communicate with external TCP services.

## Important APIs, Types, and Functions
`SimExternalConnection` inherits `IConnection` and `ReferenceCounted<SimExternalConnection>`. It exposes `close`, handshake methods, readability/writability futures, `read`, `write`, peer/debug accessors, `getSocket`, static endpoint resolution helpers, and static `connect`.

## Control Flow
The header establishes the interface contract; implementation is in the `.cpp`. Construction is private and only available to `makeReference` and `SimExternalConnectionImpl`, ensuring sockets are moved into reference-counted connection objects through the factory path.

## State and Persistence Behavior
The object owns a Boost TCP socket, debug UID, buffered read deque, and an `AsyncTrigger` for readability. State is in-memory and connection-scoped.

## Dependencies and Integration Points
It depends on Flow reference counting, `flow/network.h`, `flow/flow.h`, `flow/IConnection.h`, and Boost.Asio. It plugs into `INetworkConnections` implementations that need an `IConnection` reference.

## Risks and Edge Cases
The header exposes the raw Boost socket through `getSocket`, so callers can bypass `IConnection` sequencing. The trusted-peer answer is implemented as unconditional in the `.cpp`, so auth-sensitive callers should not mistake this adapter for a secure transport.

## Test Signals
The companion `.cpp` unit tests exercise construction, connect, read/write, DNS resolution, and hostname resolution through this declared interface.
