# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/invoker/RootCARotationHandlerInvoker.java

Purpose: Generated invoker for HA replication of root CA rotation protocol state.

Important APIs and types: Replicated methods are `rotationPrepare`, `rotationPrepareAck`, `rotationCommit`, and `rotationCommitted`. Local operations include `resetRotationPrepareAcks`, `rotationPrepareAcks`, and `setSubCACertId`.

Control flow: Most rotation transitions use `invokeReplicateDirect`; `rotationPrepareAck` uses `invokeReplicateClient`, allowing client-style submission to the current Raft group. Local dispatch casts string ids and returns ack counts when requested.

State and persistence behavior: The invoker does not persist itself; underlying root CA rotation handler tracks sub-CA id and prepare/commit acknowledgements, which must remain consistent across SCMs.

Dependencies and integration points: Integrates SCM security/certificate rotation workflows with `ScmInvoker`, string codecs, and Ratis client/direct submission paths.

Risks and test signals: Rotation is distributed and ordering-sensitive. Tests should cover prepare, ack, commit, committed paths, client/direct routing differences, ack count reset/local query, and not-leader/timeout translation.
