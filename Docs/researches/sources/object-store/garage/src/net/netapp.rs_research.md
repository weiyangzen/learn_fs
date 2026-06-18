# sources/object-store/garage/src/net/netapp.rs

## Purpose
This file implements `NetApp`, the main authenticated peer-to-peer RPC connection manager. It owns node identity, network key, version tag, connection maps, endpoint registry, listener lifecycle, outgoing connection setup, and connection/disconnection callbacks.

## Important APIs, types, and functions
Type aliases `NodeID`, `NodeKey`, and `NetworkKey` wrap sodiumoxide public/secret/auth keys. `VersionTag` combines `NETAPP_VERSION_TAG` and application version. `HelloMessage` advertises server address/port. `NetApp::new`, `on_connected`, `on_disconnected`, `endpoint`, `listen`, `drop_all_handlers`, `try_connect`, `disconnect`, connection registration callbacks, and `EndpointHandler<HelloMessage>` are key APIs. `set_keepalive` configures TCP keepalive.

## Control flow
`new` derives local node ID from the private key, builds the version tag, creates the Hello endpoint, and registers itself as handler. `listen` binds TCP, accepts connections until `must_exit`, sets keepalive, and spawns `ServerConn::run` tasks collected by a `FuturesUnordered` collector. `try_connect` avoids self/already-connected peers, optionally binds outgoing sockets, applies a 10-second connect timeout, sets keepalive, and initializes `ClientConn`. Client connection registration replaces old outgoing connections, calls callbacks, and sends Hello if listening. Server-side registration waits for Hello before exposing a usable incoming peer address.

## State and persistence behavior
All connection/endpoint state is in memory under `RwLock` or `ArcSwapOption`. There is no persistence; peering reconstructs connections from bootstrap/gossip. Version tags are exchanged per connection.

## Dependencies and integration points
It depends on tokio TCP, socket2 keepalive, sodiumoxide keys, kuska handshake via client/server modules, endpoints/messages, and peering callbacks. `garage_rpc::System` builds on `NetApp`; model K2V and table RPCs create endpoints through it.

## Risks and edge cases
Duplicate endpoint paths panic. `listen` unwraps bind failure, so caller must ensure config validity before spawning. `drop_all_handlers` is needed to break reference cycles on shutdown. Incoming connections are not treated as full peers until Hello provides address/port. Outgoing connection replacement closes the old connection asynchronously. Version tag mismatch prevents mixed incompatible nodes from connecting.

## Test signals
Network integration tests should cover handshake, listener shutdown, local/remote endpoint calls, Hello behavior, duplicate endpoint panic, connection replacement, keepalive failures as warnings, and version mismatch.
