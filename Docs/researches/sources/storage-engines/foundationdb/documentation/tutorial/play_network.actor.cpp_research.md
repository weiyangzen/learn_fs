# sources/storage-engines/foundationdb/documentation/tutorial/play_network.actor.cpp

## Purpose
Minimal Flow client/server network playground that reverses a string over request/reply streams.

## Important APIs, Types, and Functions
`PlayServerInterface` contains `getInterface` and `play`. `GetInterfaceRequest` returns the interface, and `PlayRequest` carries `msg` plus `ReplyPromise<std::string>`. `server()` handles requests, `client()` sends `"Hello World"`, and `actors` maps `serverActor`/`clientActor`.

## Control Flow
`main()` parses server/client flags, initializes Flow transport, binds in server mode, starts selected actors, and runs until all actors complete. The server loops forever over interface/play requests; the client resolves the well-known endpoint and waits for one response.

## State and Persistence Behavior
All state is transient: server interface, request payloads, response strings, and network addresses. No durable storage.

## Dependencies and Integration Points
Depends on Flow networking, request streams, reply promises, well-known endpoints, `FlowTransport`, `NetworkAddress`, TLS config, and actor compiler output. Built as `play_network`.

## Risks
Command-line parsing appears flawed: actor names fall into an `else` branch with `assert(false)`, so documented invocations can assert in debug builds. Missing-argument messages mention opposite flags. Server mode never exits normally.

## Test Signals
Build and run server/client commands, verifying the client prints `dlroW olleH`. Add regression coverage for command-line actor selection and bind failure handling.
