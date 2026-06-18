# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/replicas/BlockExistenceVerifier.java

Purpose: `BlockExistenceVerifier` implements the `blockExistence` replica verification check by making `getBlock` calls to a chosen datanode for each key location.

Important APIs and types: It implements `ReplicaVerifier`, creates a `ContainerOperationClient` and `XceiverClientManager`, uses `Pipeline.copyForReadFromNode`, `ContainerProtocolCalls.getBlock`, `OmKeyLocationInfo`, and `BlockVerificationResult`.

Control flow: `verifyBlock` builds a pipeline targeting the given datanode, acquires a read client, calls `getBlock` with block ID, token, and replica indexes, treats a response with `BlockData` as pass, otherwise returns a completed failed check, and releases the client in `finally`.

State and persistence behavior: The verifier has no persistence; state is the network client manager and response result.

Dependencies and integration points: It is selected by `ReplicasVerify --block-existence` and runs against a live cluster through SCM/datanode container protocols.

Risks: The `finally` releases `client` even if acquisition failed; release behavior must tolerate null. IO failures are marked incomplete rather than failed checks. Correctness depends on the key location token and pipeline metadata being current.

Test signals: Tests should cover pass, missing block data, IO exception, client release, and correct targeting of a single datanode.
