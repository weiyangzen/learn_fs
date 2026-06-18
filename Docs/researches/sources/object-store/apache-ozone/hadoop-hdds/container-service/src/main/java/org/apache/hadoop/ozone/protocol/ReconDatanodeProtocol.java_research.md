# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/ReconDatanodeProtocol.java

Purpose: protocol marker for datanode communication with Recon, reusing the SCM datanode protocol shape while binding a Recon Kerberos principal.

Important APIs and types: the interface extends `StorageContainerDatanodeProtocol` without adding methods. `@KerberosInfo` points to `OZONE_RECON_KERBEROS_PRINCIPAL_KEY`, and `@InterfaceAudience.Private` marks it internal.

Control flow and state: none locally.

Dependencies and integration: used by RPC/protocol wiring where Recon receives datanode reports and heartbeats using SCM-compatible protobuf messages but distinct service authentication.

Risks and test signals: the main risk is security principal mismatch. Tests should verify RPC binding uses Recon's principal and that all inherited protocol methods remain compatible.
