# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/stream/StreamingClient.java

Purpose: Netty client wrapper that requests a stream ID and stores received files through a `StreamingDestination`.

Important APIs and functions: constructors configure a `Bootstrap`, `NioEventLoopGroup`, receive buffer, keepalive, optional TLS handler, `StringEncoder`, and `DirstreamClientHandler`. `stream(String)` uses a default 200 second timeout. `stream(String, long, TimeUnit)` connects, writes `id + "\n"`, waits for channel close, verifies the handler saw the end marker, and throws `StreamingException` on timeouts or interruption. `close` shuts down the event loop group.

Control flow and state: a single handler instance is tied to the client instance, so repeated streams reuse handler state. The channel is closed in finally if still active.

Dependencies and integration: pairs with `StreamingServer` and `DirstreamServerHandler`. Optional Netty `SslContext` supports TLS.

Risks and test signals: the large fixed event-loop size and reused handler state are notable. Tests should cover success, write timeout, close timeout, missing end marker, interrupted wait, TLS pipeline insertion, repeated stream calls, and close cleanup.
