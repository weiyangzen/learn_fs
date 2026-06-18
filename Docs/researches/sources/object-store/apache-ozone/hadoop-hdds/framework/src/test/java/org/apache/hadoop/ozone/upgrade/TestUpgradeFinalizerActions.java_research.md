# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/upgrade/TestUpgradeFinalizerActions.java

Purpose: Test scaffolding for upgrade finalizer action behavior.

Important APIs/types/functions: `MockUpgradeFinalizer`, `MockLayoutVersionManager`, enum `MockLayoutFeature`, `MockLayoutFeature.addAction`, `MockLayoutFeature.action`, and `MockFailingUpgradeAction`.

Control flow: Mock finalizer overrides pre/post/finalize methods as no-ops. Mock layout manager initializes with the enum feature set. Mock layout features expose layout versions and optional attached actions. Failing action throws an `IllegalStateException` when executed.

State and persistence behavior: In-memory mock layout version state and per-enum optional action field; no persistence.

Dependencies and integration points: Integrates with `BasicUpgradeFinalizer`, `AbstractLayoutVersionManager`, `LayoutFeature`, `HDDSUpgradeAction`, and `MockComponent`.

Risks: Enum action field is mutable and shared across tests, so tests using it must reset state to avoid contamination.

Test signals: Provides reusable fixtures for action success/failure and feature version ordering in upgrade tests.
