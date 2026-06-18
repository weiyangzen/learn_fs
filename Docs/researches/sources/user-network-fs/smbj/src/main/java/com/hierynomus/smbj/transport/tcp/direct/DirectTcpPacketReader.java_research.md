<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/direct/DirectTcpPacketReader.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/direct/DirectTcpPacketReader.java

Purpose: Blocking direct TCP packet reader that reads SMB direct TCP headers and packet bodies from an InputStream.

Important APIs/types/functions: doRead(), readTcpHeader(), readPacket(int), and readFully(byte[]).

Control flow: doRead reads the 4-byte direct TCP header, parses the first byte plus 24-bit length, reads exactly that many body bytes, and delegates to PacketFactory.read(). readFully loops until buffer filled or EOF, throwing TransportException wrapping EOFException.

State and persistence behavior: Holds PacketFactory in addition to PacketReader base state.

Dependencies and integration points: Used by DirectTcpTransport. Depends on Buffer.PlainBuffer big-endian parsing and PacketFactory.

Risks: Packet length is trusted and can allocate large arrays. readFully can block until socket timeout/close. A zero-length packet is passed to packetFactory. EOF becomes TransportException.

Test signals: Header parsing, partial stream reads, EOF during header/body, malformed length, packetFactory BufferException wrapping, and socket timeout behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/direct/DirectTcpPacketReader.java -->
