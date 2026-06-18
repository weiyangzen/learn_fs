# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/upgrade/ScmOnFinalizeActionForDatanodeSchemaV2.java

Purpose: This class is the SCM-side finalization hook for the `DATANODE_SCHEMA_V2` HDDS layout feature. It currently records that the first SCM layout-feature action was executed.

Important APIs and types: It implements `HDDSUpgradeAction<SCMUpgradeFinalizationContext>` and is annotated with `@UpgradeActionHdds(feature = DATANODE_SCHEMA_V2, component = SCM)`. The only method is `execute`.

Control flow: During layout finalization, `SCMUpgradeFinalizer.replicatedFinalizationSteps` runs `HDDSLayoutFeature.scmAction`, which can invoke this action. The method logs the layout feature name and returns.

State and persistence behavior: There is no direct state mutation or persistence in this action. The surrounding finalizer still updates the VERSION file and finalization DB metadata for the layout feature.

Dependencies and integration points: The annotation registers this action with the HDDS upgrade framework for the SCM component. The action signature allows future use of node, pipeline, storage, or configuration state from `SCMUpgradeFinalizationContext`.

Risks: Because the action is currently a no-op aside from logging, correctness depends on any required schema-v2 SCM work being either unnecessary or handled elsewhere. Future changes must remain safe on every SCM because finalization actions are replicated to followers.

Test signals: Tests should verify annotation discovery for `DATANODE_SCHEMA_V2`, successful execution during finalization, and no unintended side effects on context managers.
