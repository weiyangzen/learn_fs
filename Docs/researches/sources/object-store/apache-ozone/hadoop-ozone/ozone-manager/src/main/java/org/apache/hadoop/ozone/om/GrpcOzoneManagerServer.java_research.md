# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/GrpcOzoneManagerServer.java

## Purpose

`GrpcOzoneManagerServer` is a separate Netty/gRPC network server for the OM gRPC transport used by S3 Gateway to OM communication.

## Important APIs and Types

- Constructor resolves max inbound response size, HA-specific or default gRPC port, creates gRPC metrics, and calls `init`.
- `init` builds thread pools/event loops, constructs a `NettyServerBuilder`, adds OM service and interceptors, installs metrics transport filters, and optionally configures TLS.
- `start`, `stop`, and `getPort` control the server lifecycle.

## Control Flow

Construction reads `OZONE_OM_GRPC_MAXIMUM_RESPONSE_LENGTH`, tries HA-suffixed `OZONE_OM_GRPC_PORT_KEY` using service ID and node ID, falls back to `GrpcOmTransportConfig`, creates metrics, then initializes the server. Initialization reads read-thread, boss-group, and worker-group sizes, creates daemon thread factories, creates `NioEventLoopGroup`s, builds a Netty server for the selected port with inbound size limit and executor, wraps `OzoneManagerServiceGrpc` with client-address and request/response metrics interceptors, and adds a metrics transport filter. If security and gRPC TLS are enabled, it builds a server SSL context from the certificate client's key manager, configured TLS provider, protocols, and ciphers; failures are logged but do not prevent building a non-TLS server.

`start` starts the server and updates `port` from the bound port. `stop` shuts down read executors, waits for gRPC shutdown, gracefully shuts down boss and worker event loops, logs, and always unregisters metrics.

## State and Persistence

The class holds process-local network server state: port, max size, metrics source, executor, event loop groups, and gRPC `Server`. It does not persist data.

## Dependencies and Integration Points

It integrates with OM protocol translator, `OzoneManagerServiceGrpc`, delegation token secret manager, certificate client/TLS config, gRPC Netty, Netty NIO event loops, gRPC metrics interceptors/filters, OM HA config suffixes, and `GrpcOmTransport` config.

## Risks and Edge Cases

TLS setup exceptions are logged but the server still starts without TLS if builder creation continues, which may be risky when TLS is expected. `stop` assumes all lifecycle fields are initialized and may throw unchecked exceptions if called after partial construction failure. Interrupted shutdown logs but does not re-interrupt the thread. The executor uses an unbounded queue, so slow request handling can accumulate memory pressure.

## Test Signals

Tests should cover HA and non-HA port resolution, start on port 0, interceptor/metrics registration, TLS enabled/disabled paths, graceful stop, and failure behavior when certificate/TLS setup fails.
