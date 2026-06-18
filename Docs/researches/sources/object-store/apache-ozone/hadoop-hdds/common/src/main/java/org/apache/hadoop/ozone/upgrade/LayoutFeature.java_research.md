# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/upgrade/LayoutFeature.java

## Purpose

`LayoutFeature` is the generic Ozone interface for versioned layout features used during upgrades. It connects feature metadata, layout versioning, and optional upgrade actions.

## APIs and control flow

Implementations provide `name`, `layoutVersion`, and `description`. The default `action()` returns `Optional.empty()`, allowing features without prerequisite work. The nested `UpgradeAction<T>` interface exposes a default action name from the implementation class and an `execute(T arg)` method that can throw any exception. `version()` satisfies `Versioned` by returning `layoutVersion()`.

## State, dependencies, and integration

The interface has no state. It depends on Java `Optional` and Ozone `Versioned`. It integrates with layout-version managers and finalization flows that enumerate features, compare versions, and execute feature-specific actions before finalization.

## Risks and test signals

`UpgradeAction` is generic but `action()` erases the argument type as `Optional<? extends UpgradeAction>`, so runners must coordinate argument types carefully. Tests should cover feature ordering by version, optional action execution, action failure propagation, and compatibility between feature enums and layout-version managers.
