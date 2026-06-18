# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/stream/StreamingServer.java

Purpose: Netty server wrapper for raw directory streaming.

Important APIs and functions: constructors store source, port, and optional TLS context. `start` creates boss and worker `NioEventLoopGroup`s, configures a `ServerBootstrap` with backlog 100, optional TLS handler, `ChunkedWriteHandler`, and `DirstreamServerHandler`, binds the port, and records the actual local port. `stop` gracefully shuts down both event loops. `close` delegates to `stop`.

Control flow and state: server groups are initialized on `start`; no guard prevents multiple starts or stopping before start. The bound port may differ from requested port when zero is used.

Dependencies and integration: hosts `DirstreamServerHandler` and serves `StreamingClient` instances. It is separate from the gRPC replication server and is a lower-level raw file stream utility.

Risks and test signals: fixed event-loop sizes and missing lifecycle guards can waste resources or throw null pointer errors. Tests should cover dynamic port binding, TLS pipeline, start/stop lifecycle, interrupted bind, multiple concurrent clients, and stop before start behavior.
