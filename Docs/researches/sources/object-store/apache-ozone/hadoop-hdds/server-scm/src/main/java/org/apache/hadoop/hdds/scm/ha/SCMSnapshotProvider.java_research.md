# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMSnapshotProvider.java

Purpose: Downloads the leader SCM's RocksDB checkpoint into the local Ratis snapshot directory and exposes it as a `DBCheckpoint`.

Important APIs and types: Constructor validates SCM Ratis and snapshot directories, builds a peer-node map, and stores `CertificateClient`. `getSCMDBSnapshot` downloads a `.tar` through `InterSCMGrpcClient`, untars it, deletes the archive, and returns `RocksDBCheckpoint`. `setPeerNodesMap` and `getScmSnapshotDir` support tests.

Control flow: For each request, it creates a timestamped snapshot name, looks up leader host and gRPC port, downloads the archive synchronously via `CompletableFuture.get`, extracts to a directory, and wraps that directory.

State and persistence behavior: Writes checkpoint archives and extracted checkpoint directories under the configured SCM Ratis snapshot directory. It does not cache download clients.

Dependencies and integration points: Called by `SCMHAManagerImpl.downloadCheckpointFromLeader` and `SCMStateMachine.notifyInstallSnapshotFromLeader`; uses inter-SCM gRPC and certificate credentials.

Risks and test signals: Peer lookup, host resolution via `getInetAddress().getHostAddress`, directory preconditions, and interruption handling are important. Tests should cover missing directories, unknown leader id, download failure, tar extraction, archive deletion, and returned checkpoint path.
