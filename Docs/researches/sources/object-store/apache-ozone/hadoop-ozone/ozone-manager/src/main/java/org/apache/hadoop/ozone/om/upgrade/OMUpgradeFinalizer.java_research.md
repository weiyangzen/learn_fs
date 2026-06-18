## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/upgrade/OMUpgradeFinalizer.java

Purpose: OM service implementation of layout finalization.

Important APIs and types: extends `BasicUpgradeFinalizer<OzoneManager, OMLayoutVersionManager>`; constructor accepts version manager; overrides `finalizeLayoutFeature`.

Control flow: delegates finalization to the base class with the feature's optional action and OM storage, allowing registered `OmUpgradeAction`s to run while finalizing features.

State and persistence: persistence is via `om.getOmStorage()` through the base finalizer. This class owns no independent state.

Dependencies and integration: used by OM upgrade workflows, `OMLayoutVersionManager`, `LayoutFeature`, and storage finalization.

Risks and test signals: action execution failure should surface as `UpgradeException` through the base class. Tests should verify the correct storage object and action optional are passed, finalization advances layout version, and failed actions do not partially mark features finalized.
