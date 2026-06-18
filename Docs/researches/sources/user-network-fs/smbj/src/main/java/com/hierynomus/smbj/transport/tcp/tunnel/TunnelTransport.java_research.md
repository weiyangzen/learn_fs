<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/tunnel/TunnelTransport.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/tunnel/TunnelTransport.java

Purpose: Transport wrapper that ignores the requested remote address and connects an underlying transport to a fixed tunnel host/port, typically for SSH tunnels.

Important APIs/types/functions: write(), connect(), disconnect(), and isConnected().

Control flow: connect constructs InetSocketAddress(tunnelHost, tunnelPort) and calls the wrapped transport connect. All other operations delegate unchanged.

State and persistence behavior: Holds wrapped transport and tunnel endpoint. No persistence.

Dependencies and integration points: Created by TunnelTransportFactory around another TransportLayerFactory.

Risks: SMB higher layers still believe they are connecting to the original host while TCP goes to tunnel endpoint; name validation, signing, and server identity must tolerate that. RemoteAddress is fully ignored except for the caller's surrounding context.

Test signals: Connect uses tunnel address, write/disconnect/isConnected delegate, and behavior with direct and async underlying transports.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/tunnel/TunnelTransport.java -->
