<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMContext.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMContext.java

## Purpose

`SCMContext` is SCM's shared source of truth for HA leader state, leader readiness, Raft term, safe-mode status, finalization checkpoint, SCM reference, and thread-name prefix.

## Important APIs, Types, and Functions

Important APIs are `emptyContext`, `updateLeaderAndTerm`, `setLeaderReady`, `setFinalizationCheckpoint`, `isLeader`, `isLeaderReady`, `getTermOfLeader`, `updateSafeModeStatus`, `isInSafeMode`, `isPreCheckComplete`, `getFinalizationCheckpoint`, `getScm`, `threadNamePrefix`, and the nested `Builder`.

## Control Flow

Leader/term updates acquire the write lock, update fields, and reset leader-ready when leadership is lost. Read methods acquire the read lock. In non-HA mode, represented by `INVALID_TERM`, leader and leader-ready checks always return true. `getTermOfLeader` throws a not-leader exception from the Ratis server when called on a follower SCM with a real term.

## State and Persistence Behavior

State is in-memory and protected by a read/write lock, except finalization checkpoint is also volatile. It does not persist state itself; Ratis and safe-mode managers feed updates.

## Dependencies and Integration Points

It integrates with SCM HA manager, Ratis server, safe mode manager, background services, upgrade finalization, and thread naming for SCM services.

## Risks and Edge Cases

`emptyContext` returns leader-ready in non-HA mode even with null SCM. `getTermOfLeader` only throws when the SCM reference is a `StorageContainerManager`; otherwise a follower can return the term. Builder `build` requires SCM, but testing `buildMaybeInvalid` does not.

## Test Signals

Tests should cover non-HA defaults, leader-ready reset on follower transition, set leader ready, not-leader exception path, safe-mode status reads, finalization checkpoint updates, builder validation, and concurrent read/write behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMContext.java -->
