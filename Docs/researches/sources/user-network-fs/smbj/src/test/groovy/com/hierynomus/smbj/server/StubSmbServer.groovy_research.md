# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/server/StubSmbServer.groovy
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/server/StubSmbServer.groovy

Purpose: local SMB server fixture used by transport/integration tests. It opens a listening socket, accepts client connections, reads/writes direct TCP SMB packets, and delegates packet handling to configurable responder logic for negotiate/session/tree-connect style flows.

State and persistence: owns socket/server-thread lifecycle, port, running flag, and packet responder state; no disk persistence. Dependencies are Java networking, SMB packet/message classes, and test packet processors. Integration point is tests that need a real TCP connection without a real SMB server. Risks include thread/socket leaks, race conditions around startup/shutdown, and incomplete protocol coverage. Test signal is fixture-level and valuable for transport tests.
