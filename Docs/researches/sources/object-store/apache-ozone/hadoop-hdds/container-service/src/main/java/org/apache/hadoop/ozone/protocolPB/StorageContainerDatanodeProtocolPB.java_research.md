## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocolPB/StorageContainerDatanodeProtocolPB.java

Purpose: `StorageContainerDatanodeProtocolPB` is the Hadoop RPC protobuf service interface for datanode-to-SCM communication.

Important APIs and types: it extends `StorageContainerDatanodeProtocolService.BlockingInterface`, adds `@ProtocolInfo` for protocol name `org.apache.hadoop.ozone.protocol.StorageContainerDatanodeProtocol` version `1`, and adds `@KerberosInfo` with SCM server and datanode client principal config keys.

Control flow and state: this interface has no implementation or local state. Hadoop RPC uses the annotations and generated blocking interface to bind client and server calls.

Persistence and integration: it is an RPC contract integrated with the client-side and server-side translators, SCM security configuration, datanode Kerberos identity, and generated protobuf service definitions.

Risks and test signals: protocol name and version are compatibility-sensitive. Principal keys must match secure deployment configuration. `SCMTestUtils.startScmRpcServer()` sets the protobuf RPC engine for this interface and registers a reflective blocking service, which is the primary test signal in this subset.
