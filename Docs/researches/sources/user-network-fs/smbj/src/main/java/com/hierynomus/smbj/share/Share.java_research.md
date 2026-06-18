<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/Share.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/Share.java

Purpose: Base implementation for SMB tree-connected shares and low-level SMB2 operations used by disk, pipe, and printer share subclasses.

Important APIs/types/functions: close(), isConnected(), createFile/openFileId(), queryInfo(), setInfo(), queryDirectory(), read/readAsync(), write/writeAsync(), ioctl overloads/ioctlAsync(), sendLockRequest(), changeNotifyAsync(), receive(), equals/hashCode. Status handlers allow symlink, EOF, no-more-files/no-such-file, and already-closed statuses where appropriate.

Control flow: Constructor derives negotiated dialect and buffer sizes from TreeConnect, SmbConfig, and NegotiatedProtocol. Public and package methods build SMB2 request messages with sessionId/treeId/fileId, send through Session, wait with operation-specific timeouts, and validate statuses with supplied StatusHandler. close atomically disconnects once through TreeConnect.close().

State and persistence behavior: Holds SmbPath, TreeConnect, Session, dialect, buffer/timeout limits, sessionId/treeId, and disconnected AtomicBoolean. No persistence, but owns remote tree connection lifetime.

Dependencies and integration points: Used by DiskShare, PipeShare, PrinterShare, Open subclasses, Session, TreeConnect, SMB2 message classes, Futures, ByteChunkProvider, and SmbConfig.

Risks: send() throws if disconnected, but outstanding futures may still complete after close. IOCTL input/output sizes are strictly bounded by negotiated transact buffer. equals/hashCode ignore treeId/session, so reconnects to same SmbPath compare equal. receive wraps TransportException in SMBRuntimeException.

Test signals: Buffer-size negotiation, close idempotence, read EOF status, query directory terminal statuses, IOCTL max buffer checks, disconnected send failure, equals across reconnects, lock/change notify forwarding, and timeout paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/Share.java -->
