# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/ReconfigureProtocolPB.java

## Purpose

`ReconfigureProtocolPB` is the SCM/default protobuf RPC binding for runtime reconfiguration.

## Important APIs, Types, and Functions

It extends generated `ReconfigureProtocolService.BlockingInterface` and declares protocol name `org.apache.hadoop.hdds.protocol.ReconfigureProtocol`, version 1, and SCM Kerberos server principal.

## Control Flow

No implementation; it is the base PB interface for SCM and role-specific subinterfaces.

## State and Persistence Behavior

No state or persistence.

## Dependencies and Integration Points

Used by client/server translators and SCM RPC registration.

## Risks and Test Signals

Protocol name/version compatibility is critical for Hadoop IPC. Tests should verify generated service compatibility and SCM role proxy creation.
