<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/protocol/SecretKeyProtocolServerSideTranslatorPB.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/protocol/SecretKeyProtocolServerSideTranslatorPB.java

Purpose: `SecretKeyProtocolServerSideTranslatorPB` is the server-side protobuf adapter for SCM symmetric secret-key APIs used by datanodes and OMs.

Important APIs and types: It implements `SecretKeyProtocolDatanodePB` and `SecretKeyProtocolOmPB`. It dispatches `GetCurrentSecretKey`, `GetSecretKey`, `GetAllSecretKeys`, and `CheckAndRotate` to `SecretKeyProtocolScm`. It converts `ManagedSecretKey` objects and protobuf UUIDs.

Control flow: `submitRequest` enforces SCM leadership, then dispatches with metrics. `processRequest` switches on command type and returns the appropriate nested response. IO failures are checked for Ratis not-leader cases and then converted to protobuf status and message.

State and persistence behavior: Key state and rotation persistence live behind `SecretKeyProtocolScm`. This translator has only references to the implementation, SCM, and dispatcher.

Dependencies and integration points: It integrates SCM HA checks, security protocol RPCs, OM/datanode key consumers, `ProtobufUtils`, `ManagedSecretKey.toProtobuf`, and protocol message metrics.

Risks: `getSecretKey` returns an empty response when a key is not found instead of an explicit not-found status if the implementation returns null. Status mapping depends on enum ordinal alignment with `SCMSecretKeyException`.

Test signals: Tests should cover current-key retrieval, lookup by UUID, missing-key response shape, all-key listing, forced and non-forced rotation, leader rejection, and exception status mapping.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/protocol/SecretKeyProtocolServerSideTranslatorPB.java -->
