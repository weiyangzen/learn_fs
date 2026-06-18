# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocol/SecretKeyProtocolScm.java

## Purpose

`SecretKeyProtocolScm` specializes secret-key access for SCM-to-SCM or SCM admin operations and adds explicit key rotation.

## Important APIs, Types, and Functions

It inherits key retrieval methods and adds `checkAndRotate(boolean force)`, returning whether rotation occurred or succeeded.

## Control Flow

The rotation call is implemented server-side by SCM secret-key management and exposed by the PB translator as `Type.CheckAndRotate`.

## State and Persistence Behavior

Rotation mutates SCM secret-key state and likely persistent key stores, but this interface holds no state itself.

## Dependencies and Integration Points

It pairs with `SecretKeyProtocolScmPB`, SCM HA clients, and admin paths such as `ScmClient.rotateSecretKeys`.

## Risks and Test Signals

Forced rotation can affect all token issuers/verifiers. Tests should cover forced and non-forced rotation, authorization, and propagation to clients retrieving all non-expired keys.
