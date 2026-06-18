<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/PacketReader.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/PacketReader.java

Purpose: Base runnable for blocking transport packet-reader threads.

Important APIs/types/functions: Constructor wraps input in BufferedInputStream and creates a daemon thread. start() starts it. stop() marks stopped and interrupts. run() repeatedly calls doRead(), logs packets, and passes them to PacketReceiver.handle(); errors go to handleError().

Control flow: Subclasses implement doRead() for framing/protocol. The read loop exits on interruption, stopped flag, or transport error. If stopped triggered the error path, it suppresses handleError.

State and persistence behavior: Holds input stream, packet receiver, stopped AtomicBoolean, and daemon Thread. No persistence.

Dependencies and integration points: Extended by DirectTcpPacketReader. Depends on PacketData, PacketReceiver, and TransportException.

Risks: stop interrupts but blocking InputStream.read may not unblock until socket close. handle(packet) exceptions are not caught unless they are TransportException from doRead. Thread name captures original current thread name.

Test signals: Start/stop lifecycle, EOF error delivery, stopped suppression, buffered input wrapping, daemon flag, and subclass doRead exception behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/PacketReader.java -->
