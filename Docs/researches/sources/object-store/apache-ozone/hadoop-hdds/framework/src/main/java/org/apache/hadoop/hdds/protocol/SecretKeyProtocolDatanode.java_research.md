# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocol/SecretKeyProtocolDatanode.java

## Purpose

`SecretKeyProtocolDatanode` specializes secret-key access for datanode clients.

## Important APIs, Types, and Functions

It adds no methods beyond `SecretKeyProtocol`; its primary function is `@KerberosInfo` binding with SCM as server principal and datanode as client principal.

## Control Flow

All method behavior comes from `SecretKeyProtocol`.

## State and Persistence Behavior

No state or persistence.

## Dependencies and Integration Points

It is paired with `SecretKeyProtocolDatanodePB` and datanode-side secret-key clients.

## Risks and Test Signals

The role distinction is security policy. Tests should verify the PB protocol name/principals and that datanode clients use this interface rather than OM/SCM variants.
