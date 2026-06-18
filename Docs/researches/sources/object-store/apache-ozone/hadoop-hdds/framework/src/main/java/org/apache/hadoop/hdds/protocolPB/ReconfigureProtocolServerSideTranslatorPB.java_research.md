# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/ReconfigureProtocolServerSideTranslatorPB.java

## Purpose

This server translator exposes a `ReconfigureProtocol` implementation over SCM, OM, and datanode protobuf RPC interfaces.

## Important APIs, Types, and Functions

It implements all three PB interfaces and delegates to `impl`. Helpers convert property lists and `ReconfigurationTaskStatus` into protobuf responses.

## Control Flow

Each RPC calls the local implementation and wraps `IOException` in `ServiceException`. Status conversion writes start time always, end time only when stopped, and each property change with old/new values and optional full error message.

## State and Persistence Behavior

Only the delegate reference is stored. Reconfiguration state remains in `ReconfigurationHandler`/Hadoop base class.

## Dependencies and Integration Points

Paired with `ReconfigureProtocolClientSideTranslatorPB` and role-specific PB interfaces.

## Risks and Test Signals

Null old values are serialized as empty strings, potentially losing distinction from a real empty old value. Assertions on status map require stopped status to have non-null map. Tests should cover in-progress status, completed success/failure, deleted properties, and IOException wrapping.
