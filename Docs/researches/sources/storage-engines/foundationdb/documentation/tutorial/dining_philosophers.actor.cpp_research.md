# sources/storage-engines/foundationdb/documentation/tutorial/dining_philosophers.actor.cpp

## Purpose
Distributed Flow actor solution to Dining Philosophers. A server owns fork state; clients request and release forks before eating.

## Important APIs, Types, and Functions
`DPServerInterface` exposes `getInterface`, `getFork`, and `releaseFork`. Serializable requests are `GetInterfaceRequest`, `ForkState`, `GetForkRequest`, and `ReleaseForkRequest`. `dpClient()` runs philosopher logic, `dpServerLoop()` manages fork ownership, and `main()` selects server (`-p`) or client (`-s`) mode.

## Control Flow
Clients resolve the server endpoint, choose asymmetric fork order to avoid deadlock, then loop: get first fork, get second fork, eat, release both, delay. The server `choose`s over request streams, grants free forks, records one pending waiter for busy forks, and transfers ownership on release.

## State and Persistence Behavior
All state is in memory. Server state is `forkOwners` and `pending`. Client state includes fork order, request objects, random delays, and meal counts. No database persistence is used.

## Dependencies and Integration Points
Uses Flow actors, request streams, reply promises, well-known endpoints, `FlowTransport`, `NetworkAddress`, deterministic randomness, `fmt`, TLS/network initialization, and actor compiler output.

## Risks
Only one pending waiter per fork is supported. Invalid release paths can log without replying. Infinite loops require external termination. Client disconnect/cancellation cleanup is not implemented.

## Test Signals
Run one server and clients locally; verify all philosophers continue eating with `CAUSE_DEADLOCK=false`. Build validates serialization and actor compilation; runtime tests can check progress over a fixed window.
