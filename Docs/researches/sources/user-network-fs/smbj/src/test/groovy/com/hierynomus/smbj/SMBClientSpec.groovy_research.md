# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/SMBClientSpec.groovy
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/SMBClientSpec.groovy

Purpose: tests `SMBClient` connection caching and lifecycle behavior using `StubTransportLayerFactory` and `DefaultPacketProcessor`. It asserts the same host/port reuses a connection, different ports or hosts produce different connections, closed connections are not reused, and multiple logical opens to the same host do not prematurely disconnect the underlying connection.

State and persistence: state is the client's in-memory connection table/reference counts; no persistence. Dependencies are SMB client config and test transport stubs. Integration point is connection pooling used by higher-level session/share APIs. Risks covered include stale closed connections, host/port keying, and disconnect reference management. Test signal is good for cache semantics without real network I/O.
