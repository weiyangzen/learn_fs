# sources/storage-engines/foundationdb/documentation/tutorial/tutorial.actor.cpp

## Purpose
Main Flow tutorial executable demonstrating timers, promises, triggers, request/reply streams, streaming replies, a toy in-memory KV service, concurrent clients, and simple real FoundationDB workloads.

## Important APIs, Types, and Functions
Primitive demos: `simpleTimer`, `someFuture`, `promiseDemo`, `eventLoop`, `triggerDemo`. Network demos: `EchoServerInterface`, `EchoRequest`, `ReverseRequest`, `StreamRequest`, `StreamReply`, `echoServer`, `echoClient`. KV demos: `SimpleKeyValueStoreInterface`, `Get/Set/Clear` requests, `kvStoreServer`, `connect`, `kvSimpleClient`, `kvClient`, `multipleClients`. FDB demos: `fdbClientStream`, `fdbClientGetRange`, `fdbClient`. `actors` maps command names to actor factories.

## Control Flow
`main()` parses `-p`, `-s`, `-C`, and actor names, initializes Flow transport, binds if serving, starts selected actors, and stops when they complete. Actors demonstrate `choose`, triggers, request streams, stream replies, retry loops using `tx.onError`, and range iteration.

## State and Persistence Behavior
Most state is transient. `kvStoreServer` stores data in a local `std::map`. FDB actors read/write the database selected by `clusterFile`, with `fdbClient` writing under `/tut/`.

## Dependencies and Integration Points
Depends on Flow runtime/transport, FoundationDB native API, `CLIENT_KNOBS`, deterministic randomness, `fmt`, and actor compiler output. Integrates with local cluster files and tutorial CMake target.

## Risks
Several actors run forever. Toy KV has no durability and returns `io_error` for missing keys. `fdbClient` writes real cluster data after delay. Some comments document undocumented `ReplyPromise` constraints.

## Test Signals
Smoke finite actors, echo client/server, KV set/get, stream sequence ordering, and FDB actors only against isolated clusters with valid cluster files.
