<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/TransportLayerFactory.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/TransportLayerFactory.java

Purpose: Factory interface for creating a configured protocol TransportLayer from packet handlers and SMB config.

Important APIs/types/functions: createTransportLayer(PacketHandlers<D, P>, SmbConfig).

Control flow: Connection/client code selects an implementation such as DirectTcpTransportFactory, AsyncDirectTcpTransportFactory, or TunnelTransportFactory and calls createTransportLayer before connecting.

State and persistence behavior: Interface only; implementations may hold socket factories, channel groups, or tunnel addresses.

Dependencies and integration points: Depends on protocol Packet/PacketData/PacketHandlers/TransportLayer and SmbConfig.

Risks: Factory implementations must honor config timeouts and socket settings consistently or behavior differs by transport.

Test signals: Each implementation returns a transport with expected config propagation and can be substituted through common interface.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/TransportLayerFactory.java -->
