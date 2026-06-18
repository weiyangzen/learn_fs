# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/transport/tcp/async/AsyncDirectTcpTransportSpec.groovy
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/transport/tcp/async/AsyncDirectTcpTransportSpec.groovy

Purpose: verifies that `SMBClient` can connect through `AsyncDirectTcpTransportFactory` to the local `StubSmbServer`. Setup starts the stub server; cleanup stops it. The test builds an `SMBClient` with async transport and connects to localhost on the server port.

State and persistence: live local socket/server state during the test; no disk persistence. Dependencies are async TCP transport, SMB client config, and stub server fixture. Integration point is transport-layer connection establishment. Risks covered include async transport factory wiring, socket connect behavior, and server fixture compatibility. Test signal is limited to connect success, not sustained I/O or error paths.
