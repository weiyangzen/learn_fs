# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocol/SecretKeyProtocolOm.java

## Purpose

`SecretKeyProtocolOm` specializes secret-key access for Ozone Manager clients.

## Important APIs, Types, and Functions

It adds no methods beyond `SecretKeyProtocol`. Its role is Kerberos metadata, with SCM as server and `ozone.om.kerberos.principal` as client.

## Control Flow

Behavior is inherited from `SecretKeyProtocol`.

## State and Persistence Behavior

No state or persistence.

## Dependencies and Integration Points

It maps to `SecretKeyProtocolOmPB` and OM token verification/signing components.

## Risks and Test Signals

The hard-coded OM principal key is marked TODO to move to hdds-common. Tests should guard protocol/principal metadata and OM client wiring.
