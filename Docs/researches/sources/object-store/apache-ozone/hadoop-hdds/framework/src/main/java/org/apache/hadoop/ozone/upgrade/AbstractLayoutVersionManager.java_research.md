# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/upgrade/AbstractLayoutVersionManager.java

## Purpose

`AbstractLayoutVersionManager` is the generic base implementation for Ozone layout version managers. It tracks metadata layout version, software layout version, feature maps, upgrade state, and JMX exposure. The complete 228-line source was read for this report.

## Important APIs, Types, and Functions

Important methods are `init`, `getUpgradeState`, `setUpgradeState`, `finalized`, `getMetadataLayoutVersion`, `getSoftwareLayoutVersion`, `needsFinalization`, `isAllowed`, `getFeature`, `unfinalizedFeatures`, and `close`. It implements `LayoutVersionManager` and `LayoutVersionManagerMXBean`.

## Control Flow

`init` sets metadata version, initializes feature maps, sets software version to the highest feature layout version, rejects metadata newer than software, chooses initial upgrade state, logs the versions, and registers an MBean. `finalized` advances metadata layout version only if the finalized feature is exactly next; older features are tolerated as replay, newer-than-next features throw. Read/write locks protect version and state reads/writes.

## State and Persistence Behavior

State is in-memory and volatile/locked: metadata/software layout versions, feature maps, and upgrade state. Persistent layout version is updated elsewhere, usually through `BasicUpgradeFinalizer` and `Storage`.

## Dependencies and Integration Points

It depends on `LayoutFeature`, `UpgradeFinalization.Status`, Hadoop metrics `MBeans`, Guava `Preconditions`, and Java locks/maps. Component-specific version managers extend it with their layout feature enums.

## Risks and Edge Cases

`features.lastKey()` requires at least one feature. Feature names and layout versions must be unique. MBean registration lifecycle depends on callers invoking `close`. `featureMap` reads are not always under the lock, though maps are initialized during `init`.

## Test Signals

Tests should cover init states, metadata-newer-than-software rejection, duplicate feature rejection, finalization ordering/replay behavior, `isAllowed`, unfinalized feature snapshots, state transitions, and MBean registration/unregistration.
