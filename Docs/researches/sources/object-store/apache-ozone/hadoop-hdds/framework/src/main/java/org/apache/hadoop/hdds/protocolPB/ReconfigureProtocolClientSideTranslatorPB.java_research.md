# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/ReconfigureProtocolClientSideTranslatorPB.java

## Purpose

This client translator adapts `ReconfigureProtocol` calls to SCM, OM, or datanode protobuf RPC interfaces.

## Important APIs, Types, and Functions

`createReconfigureProtocolProxy(NodeType, InetSocketAddress, UGI, OzoneConfiguration)` selects `ReconfigureProtocolOmPB`, `ReconfigureProtocolDatanodePB`, or SCM `ReconfigureProtocolPB`. Public methods implement server name, start, status, property listing, close, and underlying proxy access.

## Control Flow

Void request protos are reused as constants. `getReconfigureStatus()` invokes RPC then reconstructs Hadoop `ReconfigurationTaskStatus` from start/end times and `GetConfigurationChangeProto` entries, mapping optional error messages to `Optional<String>`.

## State and Persistence Behavior

State is only the RPC proxy. Reconfiguration state is remote.

## Dependencies and Integration Points

It depends on Hadoop RPC, role-specific PB interfaces, `ReconfigurationTaskStatus`, and generated reconfigure protobufs.

## Risks and Test Signals

Server-side null old values are serialized as empty strings, so old null versus empty can be lost on round trip. Tests should verify role selection, in-progress status with no end time/status map, error message mapping, and exception conversion.
