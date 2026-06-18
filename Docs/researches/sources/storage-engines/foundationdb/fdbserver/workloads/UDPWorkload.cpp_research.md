# sources/storage-engines/foundationdb/fdbserver/workloads/UDPWorkload.cpp

## Purpose
`UDPWorkload` tests Flow UDP socket creation, binding, send/receive, and request/ack traffic among test clients. It records sent, received, acknowledged, and successful ping/pong counts.

## Important APIs, Types, and Functions
The workload is defined in an anonymous namespace and registered as `UDPWorkload`. It uses `IUDPSocket`, `INetworkConnections::net()->createUDPSocket()`, `NetworkAddress`, `ReadYourWritesTransaction`, `BinaryWriter`/`BinaryReader`, `PromiseStream<NetworkAddress>`, `ActorCollection`, and a serializable `Message` type with `PING` and `PONG`.

## Control Flow
`setup()` selects a local UDP port, creates and binds a server socket, and writes the serialized address under `keyPrefix + clientId`. `start()` races `delay(runFor)` with `_start()`. `_start()` reads all peer addresses from the database, then runs `clientSender()`, `serverSender()`, and `_receiver()` together. `_receiver()` handles incoming packets and queues pings for ack. `serverSender()` prioritizes queued pongs, otherwise sends pings to random remotes. `clientSender()` periodically creates or rotates connected UDP sockets and sends pings, while `clientReceiver()` records pongs until the socket changes and a grace delay expires.

## State and Persistence Behavior
Persistent database state is each client's advertised UDP address under the configured prefix. Network state is bound UDP sockets and transient connected sockets. In-memory maps count traffic by peer address.

## Dependencies and Integration Points
It integrates with Flow network UDP abstractions, FDB serialization, tester client IDs, RYW transactions for peer discovery, and actor collections for receiver lifetimes.

## Risks and Edge Cases
The constructor sets `maxPort = getOption(options, "minPort"_sr, 6000)`, which appears to read the wrong option key and can make `maxPort` equal `minPort` unless `minPort` is absent. If there is only one client, `remotes` is empty and random peer selection will fail. UDP delivery is inherently lossy, but `check()` always returns true. Metric label `Acknknowledged` is misspelled.

## Test Signals
Metrics report total sent, received, acknowledged, and successes. Assertions check packet serialization type and send byte counts. There is no correctness threshold on delivery ratios.
