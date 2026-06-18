# sources/storage-engines/foundationdb/fdbrpc/tests/fdbrpc_bench.cpp

## Purpose
`fdbrpc_bench.cpp` implements a simple fdbrpc echo throughput benchmark. It can run as a server or client against `127.0.0.1:9001`, sends fixed-size payloads through `FlowTransport`, and prints request throughput from both sides.

## Important APIs, Types, And Functions
The benchmark defines `EchoServerInterface` with `getInterface` and `echo` request streams, `GetInterfaceRequest`, and `EchoRequest`. `WLTOKEN_ECHO_SERVER` is the well-known endpoint token. `StatCounter` tracks a sliding average over recent seconds. `EchoServer` serves interface discovery, echo requests, and periodic throughput printing. `echoServer` and `echoClient` are actor entry points selected from the `actors` map. `randString` creates client payloads. `main` parses `--mode` and `--payload_size`, initializes platform/network/transport, binds the server when needed, runs selected actors, and enters the network run loop.

## Control Flow
Server mode initializes `FlowTransport` as a server, binds to `127.0.0.1:9001`, exposes a well-known `getInterface` endpoint, and then races three infinite actors: interface request handling, echo request handling, and periodic throughput logging. Client mode initializes `FlowTransport` as a client, resolves the server interface via the well-known endpoint, creates one random payload, then loops in 10 second windows sending echo requests and printing completed requests per second.

## State And Persistence Behavior
Runtime state is in-memory: global `serverAddress`, global `payload_size_bytes`, server-side `EchoServerInterface`, and a `StatCounter` vector of `(timestamp, count)` buckets. There is no persistence. The process owns `g_network` and a single `FlowTransport` instance.

## Dependencies And Integration Points
The file depends on Boost program options, Flow platform/network/TLS primitives, fdbrpc serialization/request streams, and `FlowTransport`. It is built by `fdbrpc/tests/CMakeLists.txt` as `fdbrpc_transport_bench` and linked with `boost_target_program_options`.

## Risks And Test Signals
`randString` reseeds `std::rand` on every call, harmless for one payload but poor if reused in a loop. `EchoServerInterface::serialize` serializes only `echo`, likely because `getInterface` is well-known, but this is a coupling worth preserving. The benchmark uses fixed port `9001`, so local conflicts cause bind failures. Actors run indefinitely and rely on process termination. Useful signals are successful server bind, client interface discovery, repeated `Sent N requests` logs, and server `Throughput` logs.
