# sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/connection/ConnectionTest.java
# sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/connection/ConnectionTest.java

Purpose: JUnit tests for lower-level `Connection` behavior. It uses stub transport/packet processors to validate connection setup, negotiated protocol data, send/receive behavior, close behavior, or error propagation depending on scenario coverage.

State and persistence: in-memory connection state, negotiated protocol, sequence/window state, and stub transport connectivity. Dependencies are SMBJ connection classes, test packet processors, stub auth/transport, and JUnit/Mockito. Integration point is the central object used by sessions and shares. Risks covered include incorrect lifecycle flags, stale transport state, and status propagation. Test signal complements the Spock `ConnectionSpec` with Java-side coverage.
