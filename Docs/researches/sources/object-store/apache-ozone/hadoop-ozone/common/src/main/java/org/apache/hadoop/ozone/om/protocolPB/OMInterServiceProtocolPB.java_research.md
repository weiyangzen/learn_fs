# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/OMInterServiceProtocolPB.java

Purpose: Hadoop RPC protobuf binding for OM inter-service operations.

Important APIs and types: Private interface annotated with protocol name `org.apache.hadoop.ozone.om.protocol.OMInterServiceProtocol`, protocol version 1, OM Kerberos principal, and generated `OzoneManagerInterService.BlockingInterface`.

Control flow: No runtime logic in the interface. Hadoop RPC reads annotations and dispatches generated blocking methods implemented by server-side OM inter-service code.

State and persistence behavior: Stateless type declaration. Any cluster membership or bootstrap persistence occurs in server code.

Dependencies and integration points: Used by `OMInterServiceProtocolClientSideImpl`, Hadoop PB RPC server registration, and OM HA/security configuration.

Risks: The protocol metadata is a wire compatibility boundary. Generated service method changes must remain aligned with the Java interface and server translator.

Test signals: Proxy construction and successful `bootstrap` invocation over Hadoop RPC are the main integration signals.
