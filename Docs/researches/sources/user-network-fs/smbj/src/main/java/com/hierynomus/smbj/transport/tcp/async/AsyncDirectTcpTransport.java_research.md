<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/async/AsyncDirectTcpTransport.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/async/AsyncDirectTcpTransport.java

Purpose: Asynchronous direct TCP transport for SMB over port 445 using AsynchronousSocketChannel and a serialized write queue.

Important APIs/types/functions: write(P), connect(InetSocketAddress), disconnect(), isConnected(), setSoTimeout(), prepareBufferToSend(), writeOrEnqueue(), and startAsyncWrite().

Control flow: write serializes a packet to a ByteBuffer with a 4-byte direct TCP header, queues it, and starts an async write if none is active. Completion handler continues writing the current buffer until exhausted, removes completed buffers, and advances the queue. connect waits up to a fixed 5000 ms for socket connect, marks connected, and starts AsyncPacketReader. disconnect marks disconnected and closes the channel.

State and persistence behavior: Holds handlers, socketChannel, AsyncPacketReader, connected AtomicBoolean, soTimeout, LinkedBlockingQueue of ByteBuffers, and writingNow AtomicBoolean.

Dependencies and integration points: Created by AsyncDirectTcpTransportFactory. Uses PacketHandlers serializer/factory/receiver and AsyncPacketReader/PacketBufferReader.

Risks: startAsyncWrite throws IllegalStateException from async path if disconnected. Failed writes on non-closed exceptions call startNextWriteIfWaiting then handleError, so subsequent writes may continue despite error. No explicit backpressure limit on writeQueue. Connect timeout is fixed, not from config.

Test signals: Header encoding, partial async writes, queue ordering, connect timeout, write before connect, disconnect during write, receiver error on failure, and large packet serialization.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/async/AsyncDirectTcpTransport.java -->
