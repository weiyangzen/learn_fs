<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/csi/src/main/java/org/apache/hadoop/ozone/csi/CsiServer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/csi/src/main/java/org/apache/hadoop/ozone/csi/CsiServer.java

Final split target: `Docs/researches/sources/object-store/apache-ozone/hadoop-ozone/csi/src/main/java/org/apache/hadoop/ozone/csi/CsiServer.java_research.md`.

## Purpose
Hidden `ozone csi` daemon entrypoint that loads Ozone CSI configuration, creates an Ozone RPC client, and hosts Identity, Controller, and Node CSI services over a Unix domain socket. The file has 177 lines and was read in full for this research pass.

## Important APIs, Types, And Functions
Types/classes: `CsiServer, CsiConfig`. Methods and hooks: `call, main, getSocketPath, getVolumeOwner, setVolumeOwner, setSocketPath, getDefaultVolumeSize, setDefaultVolumeSize, getS3gAddress, setS3gAddress, getMountCommand`. Test annotations present: `0`.

## Control Flow
The CLI loads `CsiConfig`, starts a shutdown banner, opens an Ozone RPC client, validates `ozone.csi.owner`, builds a Netty domain-socket gRPC server with epoll event loops, starts it, waits forever, and closes the client after termination.

## State And Persistence Behavior
Persistent external state is Ozone/S3 bucket creation/deletion and host mount table changes; in-memory state is limited to configuration fields, Ozone client handles, and gRPC server lifecycle.

## Dependencies And Integration Points
imports `io.grpc.Server`, `io.grpc.netty.NettyServerBuilder`, `io.netty.channel.epoll.EpollEventLoopGroup`, `io.netty.channel.epoll.EpollServerDomainSocketChannel`, `io.netty.channel.unix.DomainSocketAddress`, `java.util.concurrent.Callable`, `org.apache.hadoop.hdds.cli.GenericCli`, `org.apache.hadoop.hdds.cli.HddsVersionProvider`; tools `goofys`.

## Risks And Edge Cases
- The shared epoll event-loop group is not explicitly shut down on exceptional startup paths.
- The service refuses startup if `ozone.csi.owner` is blank, so local configs must provide it.

## Test Signals
No direct test harness is declared in this file; validation is indirect through consumers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/csi/src/main/java/org/apache/hadoop/ozone/csi/CsiServer.java -->
