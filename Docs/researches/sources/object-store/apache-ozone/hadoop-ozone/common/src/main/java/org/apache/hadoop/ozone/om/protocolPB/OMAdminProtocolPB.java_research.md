# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/OMAdminProtocolPB.java

Purpose: Hadoop RPC protobuf binding for OM admin operations. It exposes the generated `OzoneManagerAdminService.BlockingInterface` under Hadoop's protocol metadata.

Important APIs and types: The interface is annotated with `@ProtocolInfo`, `@KerberosInfo`, and `@InterfaceAudience.Private`, and extends `OzoneManagerAdminService.BlockingInterface`.

Control flow: There is no executable logic. Hadoop RPC uses the annotations to identify the protocol name/version and OM Kerberos principal when client and server create proxies.

State and persistence behavior: Stateless interface. Persistence is handled by server implementations of the generated admin service.

Dependencies and integration points: Consumed by `OMAdminProtocolClientSideImpl`, OM admin server-side translator code, Hadoop RPC, and security setup using `OMConfigKeys.OZONE_OM_KERBEROS_PRINCIPAL_KEY`.

Risks: Protocol name and version are compatibility contracts. Changing either can break RPC negotiation. The class comment says communication between OMs, but the protocol name is admin protocol; docs should not be treated as behavioral authority.

Test signals: RPC integration tests should confirm clients can create proxies, authenticate with the configured OM principal, and invoke generated admin service methods through this PB interface.
