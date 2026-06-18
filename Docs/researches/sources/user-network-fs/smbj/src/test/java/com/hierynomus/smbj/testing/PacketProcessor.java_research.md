# sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/testing/PacketProcessor.java
# sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/testing/PacketProcessor.java

Purpose: test packet-processing abstraction and default SMB response generator. API surface includes `PacketProcessor.process(SMB2Packet)`, `NoOpPacketProcessor`, wrapper support for lambdas/custom processors, and `DefaultPacketProcessor` handling negotiate, session setup, logoff, tree connect, tree disconnect, and fallback error responses.

State and persistence: stateless processors except wrapper delegate references. Dependencies are SMB2 packet/message classes, `NtStatus`, dialect/capability fields, and security-mode/session setup data. Integration point is stub transport and high-level client tests. Risks include default responses diverging from what client setup expects, hiding errors with overly permissive responses, and incomplete command coverage. Test signal is helper infrastructure.
