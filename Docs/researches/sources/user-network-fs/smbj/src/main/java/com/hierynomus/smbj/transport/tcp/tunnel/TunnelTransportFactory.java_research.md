<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/tunnel/TunnelTransportFactory.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/tunnel/TunnelTransportFactory.java

Purpose: Factory that wraps another transport factory in TunnelTransport with a fixed host/port endpoint.

Important APIs/types/functions: Constructor stores tunnelFactory, tunnelHost, and tunnelPort. createTransportLayer() creates the underlying transport and wraps it.

Control flow: Used in config to layer tunnel address rewriting around any packet transport implementation.

State and persistence behavior: Holds tunnel factory and endpoint only.

Dependencies and integration points: Implements TransportLayerFactory and composes DirectTcpTransportFactory or AsyncDirectTcpTransportFactory.

Risks: Does not validate port range or host. Underlying factory exceptions propagate directly.

Test signals: Underlying factory invocation, wrapper endpoint propagation, delegate transport behavior, and invalid endpoint handling at connect.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/tunnel/TunnelTransportFactory.java -->
