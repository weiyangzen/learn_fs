# sources/storage-engines/foundationdb/fdbrpc/HTTPServer.cpp

`HTTPServer.cpp` implements a simulated HTTP server framework and colocated tests for the HTTP request/response layer.

Important functions are `callbackHandler()`, `connectionHandler()`, `listenActor()`, `HTTP::SimServerContext::registerNewServer()`, and `HTTP::SimRegisteredHandlerContext` DNS update helpers. Test handlers include `AlwaysFailRequestHandler`, `HelloWorldRequestHandler`, `HelloErrorRequestHandler`, and `HelloBadMD5RequestHandler`.

A simulator server registers listen addresses, starts `listenActor()`, accepts connections, and launches `connectionHandler()`. Each connection accepts the handshake, loops waiting for readability, starts request parsing, and adds callback actors. `callbackHandler()` waits for parse completion, invokes the request handler, converts known HTTP errors into 500 responses or retryable connection termination, then writes the response under a `FlowMutex` to avoid concurrent writers on a shared connection. Registered handler contexts maintain mock DNS address lists.

All state is in-memory: server actor collections, listeners, registered address lists, per-connection mutexes, and request futures. Dependencies include `fdbrpc/HTTP.h`, `INetworkConnections`, simulator mock DNS, Flow actors, `IConnection`, deterministic random, and unit-test registration.

Risks include incomplete certainty around pipelined/multiple requests per connection, error normalization boundaries, response mutex correctness, and reliance on client-side checksum validation for bad-MD5 behavior. Test signals are `/HTTP/Server/HelloWorld`, `/HTTP/Server/HelloError`, and `/HTTP/Server/HelloBadMD5`, all simulation-only.
