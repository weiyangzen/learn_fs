<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/InterSCMGrpcProtocolService.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/InterSCMGrpcProtocolService.java

## Purpose

`InterSCMGrpcProtocolService` hosts the gRPC endpoint that serves SCM DB checkpoints to peer SCMs in HA deployments.

## Important APIs, Types, and Functions

Public methods are `getPort`, `start`, and `stop`. Construction binds an `InterSCMGrpcService` implementation to a Netty gRPC server and optionally configures mutual TLS.

## Control Flow

The constructor reads the gRPC port, builds a Netty server with max inbound chunk size, adds the checkpoint service, and configures server TLS with SCM certificate key/trust managers when enabled. `start` is idempotent through `AtomicBoolean` and starts the server. `stop` shuts down and awaits termination.

## State and Persistence Behavior

State is in-memory server, port, and start flag. The service streams checkpoint data from SCM metadata store but this wrapper does not persist data.

## Dependencies and Integration Points

It integrates with `StorageContainerManager`, `InterSCMGrpcService`, SCM security config, certificate client, Netty gRPC, and SCM HA bootstrap/snapshot transfer.

## Risks and Edge Cases

TLS setup failures throw runtime exceptions after logging. `stop` only acts when the start flag is true. Server construction is package-private, so lifecycle is controlled by SCM HA components.

## Test Signals

Tests should cover start idempotence, stop after start, configured port, TLS enabled/disabled setup, TLS setup failure, max message size, and checkpoint service registration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/InterSCMGrpcProtocolService.java -->
