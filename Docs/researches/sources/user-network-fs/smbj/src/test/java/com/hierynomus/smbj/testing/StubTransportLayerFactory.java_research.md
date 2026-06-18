# sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/testing/StubTransportLayerFactory.java
# sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/testing/StubTransportLayerFactory.java

Purpose: in-memory transport factory used to run SMB client flows without sockets. `createTransportLayer` returns `StubTransportLayer`, whose `write` method processes a packet with a `PacketProcessor`, wraps it as `StubPacketData`, and feeds it back to the registered receiver. It also tracks `connected`, supports connect/disconnect/isConnected, and uses `StubMessageConverter` to return already-built packets.

State and persistence: in-memory connected flag, packet receiver, processor, and packet data; no persistence. Dependencies are protocol transport interfaces, SMB2 converter/data/header classes, and packet handlers. Integration point is most SMBJ unit/integration tests. Risks include synchronous behavior hiding real transport timing, converter bypasses, and limited error modeling. Test signal is infrastructure-critical.
