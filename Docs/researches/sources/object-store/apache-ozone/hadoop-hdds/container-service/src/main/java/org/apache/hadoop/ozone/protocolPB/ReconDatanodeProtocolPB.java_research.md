## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocolPB/ReconDatanodeProtocolPB.java

Purpose: `ReconDatanodeProtocolPB` is the protobuf RPC interface used by datanodes when talking to Recon, reusing the storage-container datanode protocol surface.

Important APIs and types: it extends `StorageContainerDatanodeProtocolPB` and adds Hadoop RPC annotations: `@ProtocolInfo` with protocol name `org.apache.hadoop.ozone.protocol.ReconDatanodeProtocol` and version `1`, plus `@KerberosInfo` with Recon server principal and datanode client principal.

Control flow and state: it is an interface with no methods beyond the inherited PB blocking interface. Runtime behavior is supplied by Hadoop RPC and the inherited protocol translator/service implementation.

Persistence and integration: this is an RPC binding contract, not persisted state. It integrates with Recon, datanode authentication, `HddsConfigKeys.HDDS_DATANODE_KERBEROS_PRINCIPAL_KEY`, and Recon configuration principal keys.

Risks and test signals: because it inherits SCM datanode PB methods, authorization and endpoint routing must ensure calls intended for Recon are served by Recon implementations. Principal misconfiguration will break secure RPC. No direct tests are in this subset.
