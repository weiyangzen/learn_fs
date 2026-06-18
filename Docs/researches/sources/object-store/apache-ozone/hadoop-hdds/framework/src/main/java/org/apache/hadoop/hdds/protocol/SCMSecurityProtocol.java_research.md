# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocol/SCMSecurityProtocol.java

## Purpose

`SCMSecurityProtocol` defines SCM CA and certificate-management RPCs used by datanodes, OMs, SCM peers, and administrative clients.

## Important APIs, Types, and Functions

It includes certificate issuance for datanodes, OMs, SCM nodes, and generic nodes; lookup by serial; CA/root CA retrieval; certificate listing; all-root-CA retrieval; and expired-certificate removal. Kerberos server principal is SCM.

## Control Flow

The interface has no implementation. Clients submit requests through `SCMSecurityProtocolClientSideTranslatorPB`; SCM-side services validate CSRs, issue certificates, and query metadata.

## State and Persistence Behavior

Persistent behavior is in SCM certificate metadata stores, not this interface. Returned values are PEM strings or lists of PEM strings.

## Dependencies and Integration Points

It uses HDDS protobuf node identity types, `HddsProtos.NodeType`, and SCM security exceptions via translators.

## Risks and Test Signals

Certificate issuance is security-sensitive: role-specific identity validation, renewal, and CA list ordering must be tested. Translator tests should verify status-to-exception mapping and correct request type selection.
