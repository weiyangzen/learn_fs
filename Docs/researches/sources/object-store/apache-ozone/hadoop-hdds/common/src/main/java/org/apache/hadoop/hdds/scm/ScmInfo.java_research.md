# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/ScmInfo.java

## Purpose
DTO returned by SCM info calls, containing cluster ID, SCM ID, and HA peer role/address strings.

## Important APIs, Types, And Functions
`ScmInfo` is final with getters for `clusterId`, `scmId`, and unmodifiable `peerRoles`. Nested `Builder` accumulates fields and copies peer roles with `setPeerRoles(List<String>)`.

## Control Flow
Callers build `ScmInfo` from SCM runtime metadata and expose it via client/admin APIs.

## State And Persistence
Instances are immutable after construction except the builder's list before build. The constructor wraps the passed list, so later builder mutation can affect the instance if the same list object is reused internally.

## Dependencies And Integration Points
Integrates with SCM client/admin service responses and HA role reporting.

## Risks And Test Signals
The constructor uses `Collections.unmodifiableList(peerRoles)` without copying; builder mutation after build could leak. Tests should verify immutability expectations and peer role output for single-node and HA clusters.
