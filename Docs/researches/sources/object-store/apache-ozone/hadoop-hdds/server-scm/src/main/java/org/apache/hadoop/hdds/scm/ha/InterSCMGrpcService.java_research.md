<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/InterSCMGrpcService.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/InterSCMGrpcService.java

## Purpose

`InterSCMGrpcService` is the gRPC service implementation that streams a flushed SCM RocksDB checkpoint to peer SCMs.

## Important APIs, Types, and Functions

It extends `InterSCMProtocolServiceGrpc.InterSCMProtocolServiceImplBase` and overrides `download`. Constructor initializes the transaction-info table and `SCMDBCheckpointProvider`. It uses `SCMGrpcOutputStream` for streaming response chunks.

## Control Flow

On `download`, it flushes the SCM HA transaction buffer, reads `TRANSACTION_INFO_KEY` to ensure transaction info exists, creates a gRPC output stream with the cluster ID and buffer size, and asks the checkpoint provider to write the DB checkpoint to the stream. IO failures are logged and sent through `responseObserver.onError`.

## State and Persistence Behavior

The service reads persistent SCM metadata store state and transaction info. It forces buffered transactions to disk before checkpointing. It does not store checkpoint files itself; the provider creates and cleans checkpoint snapshots.

## Dependencies and Integration Points

It integrates with `StorageContainerManager`, SCM HA transaction buffer, metadata store transaction info table, `HAUtils`, `SCMDBCheckpointProvider`, and inter-SCM gRPC protobufs.

## Risks and Edge Cases

`transactionInfo` is required non-null after flush; a missing table row fails the download. The request's flush flag is passed to the provider, but the transaction buffer is always flushed first. Runtime exceptions other than IO are not explicitly caught.

## Test Signals

Tests should cover transaction buffer flush before streaming, transaction-info lookup, provider invocation with request flush flag, successful chunk completion, IO error propagation, and missing transaction info behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/InterSCMGrpcService.java -->
