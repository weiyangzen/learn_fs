<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/protocol/SCMSecurityProtocolServerSideTranslatorPB.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/protocol/SCMSecurityProtocolServerSideTranslatorPB.java

Purpose: `SCMSecurityProtocolServerSideTranslatorPB` is the protobuf RPC server-side adapter for SCM security operations: certificate issuance, certificate lookup/listing, CA retrieval, root CA retrieval, and expired certificate cleanup.

Important APIs and types: It implements `SCMSecurityProtocolPB`, exposes `submitRequest` and `processRequest`, and delegates to `SCMSecurityProtocol`. Helper methods include `getDataNodeCertificate`, `getOMCertificate`, `getSCMCertificate`, `getCertificate` overloads, `getCACertificate`, `listCertificate`, `getRootCACertificate`, `listCACertificate`, `getAllRootCa`, and `removeExpiredCertificates`.

Control flow: `submitRequest` rejects non-leader SCMs by triggering a Ratis not-leader exception, then invokes `OzoneProtocolMessageDispatcher`. `processRequest` builds an OK response, switches on command type, populates the matching response proto, marks unsupported CRL/revoke operations as internal errors, and converts `IOException` to protocol status and message.

State and persistence behavior: The translator persists nothing directly. Certificate and CA state lives behind `SCMSecurityProtocol`. It uses SCM storage config to decide whether SCM HA/root CA fields are valid and includes root CA data only when needed.

Dependencies and integration points: It integrates SCM HA leader checks, Ratis exception translation, security protocol implementations, `ProtocolMessageMetrics`, and protobuf response status conventions.

Risks: Status mapping uses enum ordinal alignment between `SCMSecurityException` error codes and protobuf `Status`, which is fragile if enums diverge. Some operations are explicitly unsupported but still present in the switch. HA checks differ between SCM certificate and root CA requests.

Test signals: Tests should cover leader rejection, every certificate command, root CA inclusion in HA mode, non-HA errors, unsupported operations, expired removal, all-root-CA listing, and exception-to-status/message mapping.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/protocol/SCMSecurityProtocolServerSideTranslatorPB.java -->
