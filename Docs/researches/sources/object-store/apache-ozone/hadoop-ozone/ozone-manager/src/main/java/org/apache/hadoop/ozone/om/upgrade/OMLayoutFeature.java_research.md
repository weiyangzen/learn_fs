## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/upgrade/OMLayoutFeature.java

Purpose: enum of OM layout features and layout versions.

Important APIs and types: implements `LayoutFeature`; features run from `INITIAL_VERSION(0)` through `SNAPSHOT_DEFRAG(9)`. Methods expose `layoutVersion`, `description`, `addAction`, and optional `action`.

Control flow and state: enum instances hold layout version, description, and an optional `OmUpgradeAction`; `addAction` only stores the first action to avoid overwriting.

Dependencies and integration: consumed by `OMLayoutVersionManager`, layout aspects, upgrade finalizer, annotations, and service feature gates such as snapshot defrag.

Risks and test signals: ordering defines software max layout version. Adding a feature requires appending a new enum value, guarding new behavior, and optionally registering upgrade actions. Tests should verify max version, descriptions, first-action-wins, deprecated `HSYNC` handling, and that new feature numbers are monotonic.
