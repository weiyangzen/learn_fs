# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/ReconfigureProtocolDatanodePB.java

## Purpose

`ReconfigureProtocolDatanodePB` is the datanode-specific protobuf RPC interface for runtime reconfiguration.

## Important APIs, Types, and Functions

It extends `ReconfigureProtocolPB`, declares the common protocol name/version, and uses the datanode Kerberos server principal.

## Control Flow

No implementation; Hadoop RPC dispatches generated service methods through the server translator.

## State and Persistence Behavior

No state or persistence.

## Dependencies and Integration Points

Used by the client translator when `NodeType.DATANODE` is requested and by datanode RPC server registration.

## Risks and Test Signals

Incorrect principal metadata would break secure admin reconfiguration. Tests should verify role-based proxy selection and protocol annotations.
