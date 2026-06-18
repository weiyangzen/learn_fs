<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/direct/DirectTcpTransportFactory.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/direct/DirectTcpTransportFactory.java

Purpose: Factory for blocking direct TCP transports.

Important APIs/types/functions: createTransportLayer(PacketHandlers, SmbConfig) returns DirectTcpTransport configured with config socket factory and SO timeout.

Control flow: Connection code calls the factory before connect; the created transport handles actual socket lifecycle.

State and persistence behavior: Stateless factory.

Dependencies and integration points: Implements TransportLayerFactory and uses SmbConfig.getSocketFactory()/getSoTimeout().

Risks: Any config socket factory misconfiguration surfaces later at connect time. No additional validation.

Test signals: Factory returns DirectTcpTransport, propagates socket factory and timeout, and works through TransportLayerFactory interface.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/direct/DirectTcpTransportFactory.java -->
