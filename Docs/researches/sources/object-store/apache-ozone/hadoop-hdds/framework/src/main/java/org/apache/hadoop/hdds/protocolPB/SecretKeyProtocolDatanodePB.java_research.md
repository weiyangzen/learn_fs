# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/SecretKeyProtocolDatanodePB.java

## Purpose

`SecretKeyProtocolDatanodePB` binds datanode-role secret-key protobuf RPCs.

## Important APIs, Types, and Functions

It extends generated `SCMSecretKeyProtocolService.BlockingInterface`, sets protocol name `org.apache.hadoop.hdds.protocol.SecretKeyProtocolDatanode`, version 1, SCM server principal, and datanode client principal.

## Control Flow

No implementation.

## State and Persistence Behavior

No state or persistence.

## Dependencies and Integration Points

Used by datanode secret-key clients and failover providers.

## Risks and Test Signals

Principal metadata enforces the role contract. Tests should verify protocol annotations and proxy provider selection.
