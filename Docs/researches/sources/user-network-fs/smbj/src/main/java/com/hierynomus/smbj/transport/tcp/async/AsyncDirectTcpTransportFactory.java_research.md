<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/async/AsyncDirectTcpTransportFactory.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/async/AsyncDirectTcpTransportFactory.java

Purpose: Transport factory that creates AsyncDirectTcpTransport instances, optionally bound to a caller-provided asynchronous channel group.

Important APIs/types/functions: createTransportLayer(), constructors for default group, ExecutorService, or AsynchronousChannelGroup, and createGroup(ExecutorService).

Control flow: createTransportLayer constructs AsyncDirectTcpTransport with config soTimeout and packet handlers, wrapping IOException in SMBRuntimeException. Executor constructor builds an AsynchronousChannelGroup from the executor.

State and persistence behavior: Holds an AsynchronousChannelGroup reference; default null delegates to system default group.

Dependencies and integration points: Implements TransportLayerFactory and integrates with SmbConfig transport selection.

Risks: createGroup wraps IOException in RuntimeException rather than SMBRuntimeException. The factory does not own shutdown of executor/channel group. Null group behavior depends on JDK AsynchronousSocketChannel.open(null).

Test signals: Default group creation, executor group creation, IOException wrapping, soTimeout propagation, and lifecycle/shutdown ownership.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/async/AsyncDirectTcpTransportFactory.java -->
