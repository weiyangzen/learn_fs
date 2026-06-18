# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/DiskBalancerProtocolPB.java

## Purpose

`DiskBalancerProtocolPB` is the Hadoop RPC protobuf binding for datanode DiskBalancer operations.

## Important APIs, Types, and Functions

It extends `DiskBalancerProtocolService.BlockingInterface` and declares `@ProtocolInfo` with protocol name `org.apache.hadoop.hdds.protocol.DiskBalancerProtocol` and version 1. Kerberos server principal is the datanode principal.

## Control Flow

No implementation. Hadoop RPC uses the annotations and blocking interface to bind server and client translators.

## State and Persistence Behavior

No state or persistence.

## Dependencies and Integration Points

It integrates generated protobuf service code with Hadoop IPC.

## Risks and Test Signals

Protocol name/version and Kerberos principal must match clients and servers. Tests should verify translator proxy creation uses this interface and service methods are compatible with generated protobuf definitions.
