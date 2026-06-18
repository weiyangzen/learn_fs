# sources/storage-engines/foundationdb/flow/include/flow/IUDPSocket.h

## Purpose
`IUDPSocket.h` defines Flow's asynchronous UDP socket abstraction for connected and unconnected datagram communication.

## Important APIs, Types, And Functions
`IUDPSocket` declares `MAX_PACKET_SIZE`, destructor, reference counting, `close()`, `send()`, `sendTo()`, `receive()`, `receiveFrom()`, `bind()`, `getDebugID()`, `localAddress()`, and `native_handle()`.

## Control Flow
Callers create sockets through `INetworkConnections`, optionally bind them, send datagrams to a connected peer or explicit peer, and receive datagrams with or without sender address output. Operations complete through Flow futures.

## State And Persistence Behavior
Socket state is backend-owned: OS handle, bind/connect address, pending operations, and debug ID. No payload persists after future completion except caller-owned buffers.

## Dependencies And Integration Points
It depends on Boost.Asio UDP sockets and `flow/network.h`. It integrates with network backends, simulation, and any Flow component requiring datagrams.

## Risks And Edge Cases
The max UDP packet size is enforced in simulation; real networks may impose lower MTUs. Caller buffers must remain valid until futures complete. Close must unblock pending operations without use-after-free.

## Test Signals
Connected and unconnected send/receive, bind/local address, oversized packet behavior, close while pending, native handle availability, IPv4/IPv6 sockets, and simulation parity tests are useful.
