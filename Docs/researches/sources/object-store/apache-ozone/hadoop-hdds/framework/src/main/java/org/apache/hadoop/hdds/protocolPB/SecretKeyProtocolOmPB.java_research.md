# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/SecretKeyProtocolOmPB.java

## Purpose

`SecretKeyProtocolOmPB` binds OM-role secret-key protobuf RPCs.

## Important APIs, Types, and Functions

It extends generated `SCMSecretKeyProtocolService.BlockingInterface` and declares the OM protocol name/version, SCM server principal, and `ozone.om.kerberos.principal` client principal.

## Control Flow

No implementation.

## State and Persistence Behavior

No state or persistence.

## Dependencies and Integration Points

Used by OM secret-key clients and the shared client translator.

## Risks and Test Signals

Hard-coded principal key is a dependency-layering risk. Tests should verify role-specific protocol metadata and secure client wiring.
