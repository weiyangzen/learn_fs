# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/security/RootCARotationHandler.java

Purpose: `RootCARotationHandler` defines the replicated command surface for root CA and sub-CA rotation across SCM HA peers. It is an `SCMHandler` whose operations are executed through the SCM Ratis path.

Important APIs and types: The replicated methods are `rotationPrepare(rootCertId)`, `rotationPrepareAck(rootCertId, scmCertId, scmId)`, `rotationCommit(rootCertId)`, and `rotationCommitted(rootCertId)`. Additional local helpers expose ack counting, ack reset, and new sub-CA certificate ID storage. `getType()` returns `SCMRatisProtocol.RequestType.CERT_ROTATE`.

Control flow: The leader sends prepare, followers prepare a new sub-CA and acknowledge through a client-style replicated call, the leader waits for enough acks, and then commit/committed commands make peers switch certificates and clean up. Annotation metadata controls whether invocations are ordinary replicated state-machine operations or client-originating replication.

State and persistence behavior: The interface itself owns no state. Implementations persist certificate IDs, move key/cert directories, reload certificate clients, and count prepare acknowledgements.

Dependencies and integration points: It integrates root CA rotation manager scheduling with SCM HA Ratis invocation infrastructure via `SCMHandler` and `@Replicate`. It is invoked by `RootCARotationManager` and implemented by `RootCARotationHandlerImpl`.

Risks: Correctness depends on all implementations treating certificate IDs idempotently because Ratis log replay can reapply commands. Ack counting is leader-local and must not be confused with persisted rotation state.

Test signals: Tests should verify annotation-driven replication, idempotent skip behavior on already-rotated certs, ack counts, and request type routing.
