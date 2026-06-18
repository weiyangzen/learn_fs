## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/upgrade/BelongsToLayoutVersion.java

Purpose: class-level annotation marking OM request classes as belonging to an `OMLayoutFeature`.

Important APIs and types: runtime-retained annotation targeting `TYPE` with single value `OMLayoutFeature value()`.

Control flow and integration: enforced by `OMLayoutFeatureAspect.beforeRequestApplyTxn`, which checks annotated `OMClientRequest.preExecute` calls against the current OM layout version.

State, risks, and test signals: no state. Missing annotation on new layout-sensitive requests bypasses aspect gating. Tests should verify runtime retention, target type, and aspect rejection for requests annotated with future features.
