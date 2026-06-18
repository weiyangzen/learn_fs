# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestSecretKeysApi.java

## Purpose

`TestSecretKeysApi` validates the secure SCM secret-key RPC API. It covers successful key retrieval and rotation, lookup by key ID, failover consistency, authorization denial, and behavior when Hadoop security authorization is disabled.

## Important APIs, Types, And Functions

The final class sets up MiniKdc, Kerberos principals/keytabs, secure Ozone configuration, and a MiniOzone HA cluster. It uses `SecretKeyProtocol`, `ManagedSecretKey`, `getSecretKeyClientForDatanode`, `StorageContainerManager`, `RemoteException`, and `AuthorizationException`. Helpers include `setSecureConfig`, `startCluster`, `getSecretKeyProtocol`, and `enableBlockToken`.

## Control Flow

Setup starts KDC and creates credentials. `testSecretKeyApiSuccess` enables block tokens, shortens rotation windows, waits for multiple active keys, checks current/all/by-ID calls, then verifies unauthorized users are rejected. `testSecretKeyApi` checks default single-key behavior. `testSecretKeyAfterSCMFailover` shuts down the active SCM and compares keys after failover. `testSecretKeyWithoutAuthorization` confirms access when authorization is disabled.

## State And Persistence Behavior

Secret keys are persisted in SCM metadata and replicated through HA. Kerberos keytabs and MiniKdc state are temporary test artifacts. Failover validates key-list persistence across leaders.

## Dependencies And Integration Points

It integrates Hadoop security, MiniKdc, SCM secret-key protocol, block-token configuration, SCM HA, and client RPC authorization.

## Risks And Test Signals

Failures indicate security misconfiguration, unauthorized protocol access, key rotation bugs, HA replication gaps, or stale secret-key clients after failover. The happy-case test is marked flaky for HDDS-8900.
