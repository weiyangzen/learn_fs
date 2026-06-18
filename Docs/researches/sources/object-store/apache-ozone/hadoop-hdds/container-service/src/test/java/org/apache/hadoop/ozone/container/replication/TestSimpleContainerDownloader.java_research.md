## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestSimpleContainerDownloader.java

Purpose: Tests `SimpleContainerDownloader` source selection, retry across failed datanodes, async/direct failure handling, randomization, and client closure.

Important APIs/types/functions: `SimpleContainerDownloader.getContainerDataFromReplicas`, `shuffleDatanodes`, `createReplicationClient`, `downloadContainer`, `GrpcReplicationClient.close`, and nested `TestingContainerDownloader`.

Control flow: A testing subclass returns completed paths named after selected datanodes, throws immediately for configured failed datanodes, or returns futures that fail asynchronously. Happy path uses first datanode when shuffle is disabled. Failure tests verify fallback to the next datanode. Random-selection test runs many iterations and expects the second datanode to appear at least once. All clients are verified closed.

State and persistence behavior: No real downloads; returned `Path` encodes datanode UUID. Temporary directory is passed but not populated by the test subclass.

Dependencies and integration points: Supports pull replication robustness and resource cleanup around gRPC clients.

Risks and test signals: Random-selection test is probabilistic but extremely low false-failure probability. It validates retry behavior without testing actual network transfer.
