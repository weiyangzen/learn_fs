## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/upgrade/UpgradeActionOm.java

Purpose: class-level annotation linking an OM upgrade action implementation to an `OMLayoutFeature`.

Important APIs and types: runtime-retained annotation targeting `TYPE` with `OMLayoutFeature feature()`.

Control flow and integration: `OMLayoutVersionManager.registerUpgradeActions` scans for this annotation, instantiates classes implementing `OmUpgradeAction`, and attaches them to the annotated feature when not already finalized.

State, risks, and test signals: no state. Missing annotation means the action is never registered; wrong feature binds it to the wrong finalization step. Tests should verify retention, target, feature extraction, and registration behavior for annotated/non-annotated action classes.
