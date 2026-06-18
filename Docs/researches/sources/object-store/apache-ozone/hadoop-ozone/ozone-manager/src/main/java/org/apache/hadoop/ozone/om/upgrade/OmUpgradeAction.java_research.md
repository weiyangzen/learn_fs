## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/upgrade/OmUpgradeAction.java

Purpose: marker interface for OM-specific upgrade actions that execute with an `OzoneManager` argument.

Important APIs and types: extends `LayoutFeature.UpgradeAction<OzoneManager>` without adding methods.

Control flow and integration: discovered by `OMLayoutVersionManager.registerUpgradeActions` when classes are annotated with `@UpgradeActionOm`, and invoked by `OMUpgradeFinalizer` through feature actions.

State, risks, and test signals: no state. Implementations must be public/no-arg instantiable for reflection scanning. Tests should verify action discovery requires this interface and annotation.
