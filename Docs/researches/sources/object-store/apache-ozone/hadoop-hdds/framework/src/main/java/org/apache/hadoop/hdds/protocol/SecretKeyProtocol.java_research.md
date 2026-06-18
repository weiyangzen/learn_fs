# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocol/SecretKeyProtocol.java

## Purpose

`SecretKeyProtocol` exposes SCM-managed symmetric secret keys used for signing and verifying short-lived tokens.

## Important APIs, Types, and Functions

The interface defines `getCurrentSecretKey()`, `getSecretKey(UUID)`, and `getAllSecretKeys()`, returning `ManagedSecretKey` objects.

## Control Flow

It is a read-oriented RPC contract. Role-specific subinterfaces add Kerberos principal constraints; SCM-specific access adds rotation.

## State and Persistence Behavior

No local state. Implementations read from SCM secret-key state and stores.

## Dependencies and Integration Points

It integrates with HDDS symmetric key clients, token secret managers, and PB secret-key translators.

## Risks and Test Signals

Returning keys is security-sensitive; role-based Kerberos access and expired-key filtering must be enforced server-side. Tests should cover missing UUID behavior, current-key availability, and all-key list conversion.
