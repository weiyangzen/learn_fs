<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/direct/DirectTcpTransport.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/direct/DirectTcpTransport.java

Purpose: Blocking direct TCP transport implementation for SMB packets over sockets.

Important APIs/types/functions: write(P), connect(InetSocketAddress), disconnect(), isConnected(), setSocketFactory(), setSoTimeout(), writePacketData(), and writeDirectTcpPacketHeader().

Control flow: connect creates a socket through SocketFactory, sets SO_TIMEOUT, opens buffered output, starts DirectTcpPacketReader on the input. write first checks connected, takes write lock, rechecks connected, serializes packet, writes 4-byte direct TCP header, writes packet bytes, and flushes. disconnect takes write lock, stops reader, closes input/output/socket, and nulls resources.

State and persistence behavior: Holds PacketHandlers, ReentrantReadWriteLock, SocketFactory, soTimeout, Socket, BufferedOutputStream, and PacketReader.

Dependencies and integration points: Created by DirectTcpTransportFactory. Uses ProxySocketFactory by default unless config supplies another factory.

Risks: isConnected relies on socket flags and may return true after remote half-close until read detects EOF. disconnect closes socket.getInputStream() after stop; getInputStream can throw. PacketData buffer rpos is not advanced after write, which is usually fine for a serialized temporary buffer. No write timeout beyond socket behavior.

Test signals: Config socket factory, write header bytes, concurrent write/disconnect race, reader start, EOF error propagation, disconnect idempotence, and write after disconnect.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/direct/DirectTcpTransport.java -->
