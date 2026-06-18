<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/InterSCMGrpcClient.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/InterSCMGrpcClient.java

## Purpose

`InterSCMGrpcClient` downloads RocksDB checkpoints from another SCM through the inter-SCM gRPC service. It is the client-side implementation of `SCMSnapshotDownloader`.

## Important APIs, Types, and Functions

Public APIs are the constructor, `download(Path)`, `shutdown`, and `close`. Nested `StreamDownloader` implements `StreamObserver<CopyDBCheckpointResponseProto>` and adapts streamed protobuf chunks into a local file and `CompletableFuture<Path>`.

## Control Flow

Construction builds a Netty channel with plaintext by default, or mutual TLS when security and gRPC TLS are enabled. `download` sends a flush-enabled checkpoint request and returns a future. The stream observer writes each received chunk to the output stream, completes the future on `onCompleted`, and on error closes the stream, deletes the partial output, and completes exceptionally.

## State and Persistence Behavior

State includes the gRPC channel/stub, deadline timeout, output stream, and output path. Persistence is the checkpoint file written to `outputPath`; partial files are deleted on failure.

## Dependencies and Integration Points

It integrates with HA snapshot download, inter-SCM protobuf/gRPC stubs, Ozone chunk-size constants, `SecurityConfig`, SCM certificate client key/trust managers, and Netty gRPC TLS.

## Risks and Edge Cases

The deadline is read in milliseconds but applied with `TimeUnit.SECONDS`, which deserves scrutiny. Stream constructor throws unchecked IO if the output path cannot be opened. If deleting a failed partial file fails, it logs but leaves residue.

## Test Signals

Tests should cover plaintext and TLS channel setup, successful multi-chunk download, completion future path, stream open failure, on-error partial deletion and exceptional completion, close/shutdown interruption, and deadline unit behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/InterSCMGrpcClient.java -->
