<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/async/PacketBufferReader.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/async/PacketBufferReader.java

Purpose: Stateful parser for direct TCP packet framing over an async ByteBuffer stream.

Important APIs/types/functions: readNext(), getBuffer(), readPacketHeader(), readPacketBody(), and internal header/body state checks.

Control flow: readNext flips the read buffer, reads a 4-byte header when available, masks the big-endian int to 24-bit length, allocates currentPacketBytes, copies as much body data as available, compacts the buffer, and returns a full packet only when all bytes are accumulated. It resets packet state after a full packet.

State and persistence behavior: Holds a 9000-byte ByteBuffer, currentPacketBytes, currentPacketLength, and currentPacketOffset.

Dependencies and integration points: Used exclusively by AsyncPacketReader for direct TCP framing.

Risks: Packet length is trusted and can allocate very large arrays if a peer sends a malformed header. Fixed read buffer handles jumbo frame reads but packets may be larger through accumulation. Zero-length packet is possible and should be considered. Not thread-safe.

Test signals: Header split across reads, body split across reads, multiple packets in one buffer, 24-bit masking, zero-length packet, malformed huge length, and buffer compact position handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/async/PacketBufferReader.java -->
