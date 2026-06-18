# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/checksum/DNContainerOperationClient.java

## Purpose
Client wrapper for datanode-to-datanode container-level RPCs needed by container reconciliation, currently fetching remote container checksum information.

## Important APIs, Types, And Functions
Constructor builds a `TokenHelper` and `XceiverClientManager`. Public APIs expose the manager/helper, `getContainerChecksumInfo(containerId, dn)`, `createSingleNodePipeline`, and `close`.

## Control Flow
For a peer datanode, it creates a closed single-node standalone pipeline, acquires an xceiver client, obtains a container token, calls `ContainerProtocolCalls.getContainerChecksumInfo`, rejects empty serialized responses, parses the protobuf, and releases the client in a finally block.

## State And Persistence
State is the token helper and xceiver client manager/cache. No durable persistence.

## Dependencies And Integration Points
Depends on HDDS SCM client/pipeline APIs, datanode details, security config/certificate trust manager, secret-key signer, token helper, and protobuf container protocol calls.

## Risks
Security-enabled mode requires a certificate client that can create a trust manager. Empty checksum files are treated as IO failures. The client releases with `invalidate=false`, so bad connections may remain cached unless lower layers handle failures.

## Test Signals
Signals include successful checksum fetch from a peer, token generation under secure mode, empty-response failure, invalid protobuf failure, client release on exceptions, and close releasing the manager.
