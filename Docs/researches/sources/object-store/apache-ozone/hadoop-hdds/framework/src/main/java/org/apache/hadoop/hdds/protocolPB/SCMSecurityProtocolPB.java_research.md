# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/SCMSecurityProtocolPB.java

## Purpose

`SCMSecurityProtocolPB` is the Hadoop IPC protobuf binding for SCM security operations.

## Important APIs, Types, and Functions

It extends generated `SCMSecurityProtocolService.BlockingInterface` and declares protocol name `org.apache.hadoop.hdds.protocol.SCMSecurityProtocol`, version 1, and SCM Kerberos server principal.

## Control Flow

No implementation in this interface.

## State and Persistence Behavior

No state or persistence.

## Dependencies and Integration Points

Used by SCM security clients, failover proxy providers, and SCM RPC servers.

## Risks and Test Signals

Protocol annotation drift would break secure clients. Tests should verify generated service compatibility and principal metadata.
