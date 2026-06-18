# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/SecretKeyProtocolScmPB.java

## Purpose

`SecretKeyProtocolScmPB` binds SCM-role secret-key protobuf RPCs, including rotation access.

## Important APIs, Types, and Functions

It extends generated `SCMSecretKeyProtocolService.BlockingInterface`, sets protocol name `org.apache.hadoop.hdds.protocol.SecretKeyProtocolScm`, version 1, and SCM as both server and client Kerberos principal.

## Control Flow

No implementation.

## State and Persistence Behavior

No state or persistence.

## Dependencies and Integration Points

Used by SCM clients/admin paths that need key retrieval and rotation.

## Risks and Test Signals

Protocol/principal mismatches would block SCM HA/admin secret-key operations. Tests should verify metadata and rotation route selection.
