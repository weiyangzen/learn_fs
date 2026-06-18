# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/ReconfigureProtocolOmPB.java

## Purpose

`ReconfigureProtocolOmPB` is the OM-specific protobuf RPC interface for runtime reconfiguration.

## Important APIs, Types, and Functions

It extends `ReconfigureProtocolPB` with common protocol name/version and a Kerberos server principal key of `ozone.om.kerberos.principal`.

## Control Flow

No implementation in this file.

## State and Persistence Behavior

No state or persistence.

## Dependencies and Integration Points

Selected by `ReconfigureProtocolClientSideTranslatorPB` for `NodeType.OM` and implemented by `ReconfigureProtocolServerSideTranslatorPB`.

## Risks and Test Signals

The OM principal key is hard-coded due to dependency layering. Tests should protect role selection and secure RPC metadata.
