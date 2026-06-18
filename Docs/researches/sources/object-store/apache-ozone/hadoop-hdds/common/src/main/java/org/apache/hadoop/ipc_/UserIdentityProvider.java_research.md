# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/UserIdentityProvider.java

## Purpose
`UserIdentityProvider` is a simple `IdentityProvider` implementation for IPC scheduling/accounting. It groups schedulable RPC work by the short username of the call's `UserGroupInformation`.

## Important APIs, types, and functions
- `makeIdentity(Schedulable obj)` reads `obj.getUserGroupInformation()` and returns `ugi.getShortUserName()`, or `null` when no UGI is attached.

## Control flow
The implementation is branch-light: obtain the UGI, return `null` for anonymous or not-yet-authenticated calls, otherwise return the short username. Schedulers such as decay/fair-call queue components can use this identity to aggregate cost or priority by user.

## State and persistence behavior
The class is stateless and has no persistence. It depends entirely on the `Schedulable` argument.

## Dependencies and integration points
It depends on `IdentityProvider`, `Schedulable`, and Hadoop `UserGroupInformation`. It integrates with IPC schedulers that need a stable identity key.

## Risks and edge cases
Returning `null` for missing UGI must be accepted by downstream scheduler code. Short usernames intentionally collapse Kerberos realms and auth-specific identities; that is appropriate for user grouping but can merge identities that differ only by realm.

## Test signals
Tests should pass schedulables with null UGI, simple users, and Kerberos-style users where short-name mapping matters. Scheduler tests should verify null identity handling and aggregation by short username.
