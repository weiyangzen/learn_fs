<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/async/AsyncPacketReader.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/async/AsyncPacketReader.java

Purpose: Asynchronous packet reader that continuously reads direct TCP framed bytes from an AsynchronousSocketChannel and dispatches decoded packets.

Important APIs/types/functions: start(String, int), stop(), initiateNextRead(PacketBufferReader), readAndHandlePacket(), handleAsyncFailure(), isChannelClosedByOtherParty(), closeChannelQuietly().

Control flow: start stores remote host/timeout and initiates a read using PacketBufferReader's ByteBuffer. Completion processes as many complete packets as readNext() can produce, then issues another read. Negative bytes mean EOF and produce failure unless stopped. Decode errors or async failures close the channel.

State and persistence behavior: Holds packetFactory, handler, channel, remoteHost, soTimeout, and stopped AtomicBoolean.

Dependencies and integration points: Used by AsyncDirectTcpTransport. Depends on PacketBufferReader, PacketFactory, PacketReceiver, ASN-independent packet decoding, and NIO completion handlers.

Risks: handleAsyncFailure closes channel but does not call handler.handleError for read failures; unlike write failures, receiver may not learn why reads stopped. stop only flips flag, it does not close channel. Timeout failures are treated as async failures and close channel.

Test signals: Complete packet dispatch, fragmented packet assembly across reads, multiple packets per read, EOF handling, decode error handling, stop suppressing next reads, and receiver error expectations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/async/AsyncPacketReader.java -->
