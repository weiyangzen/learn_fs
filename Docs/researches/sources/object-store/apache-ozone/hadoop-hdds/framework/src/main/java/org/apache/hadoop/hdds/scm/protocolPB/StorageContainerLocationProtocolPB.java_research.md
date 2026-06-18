# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/protocolPB/StorageContainerLocationProtocolPB.java

## Purpose
`StorageContainerLocationProtocolPB` is the Hadoop RPC protobuf service interface for SCM storage-container and admin operations.

## Important APIs, Types, And Functions
It extends generated `StorageContainerLocationProtocolService.BlockingInterface` and adds Hadoop `@ProtocolInfo` for `org.apache.hadoop.hdds.scm.protocol.StorageContainerLocationProtocol` version `1`, SCM Kerberos principal metadata, and private interface audience.

## Control Flow
There is no executable implementation. Clients call the generated blocking `submitRequest` through retry proxies; servers implement the generated service contract.

## State, Persistence, And Dependencies
No state is stored. Dependencies are generated protobuf service classes, Hadoop RPC annotations, and SCM config constants.

## Integration Points
`StorageContainerLocationProtocolClientSideTranslatorPB` creates retry proxies of this type, and SCM exposes a matching protobuf server translator.

## Risks
The protocol name and version are compatibility-critical. Any mismatch between this interface and the Java protocol/translator can break client-server negotiation.

## Test Signals
Signals include successful Hadoop RPC proxy creation, protocol version negotiation, and Kerberos principal resolution.
