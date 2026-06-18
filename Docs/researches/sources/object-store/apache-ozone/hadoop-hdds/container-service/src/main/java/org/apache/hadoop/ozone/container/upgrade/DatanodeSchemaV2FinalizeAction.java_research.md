# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/upgrade/DatanodeSchemaV2FinalizeAction.java

Purpose: finalize action for the first datanode schema-version feature.

Important APIs and functions: annotated for `DATANODE_SCHEMA_V2`. `execute` logs that new containers will use schema version 2 after finalization.

Control flow and state: no local state is changed in this action. The effective schema behavior is controlled elsewhere by `VersionedDatanodeFeatures.SchemaV2.chooseSchemaVersion`.

Dependencies and integration: invoked by HDDS upgrade finalization and indirectly affects future container creation policy through the layout version manager.

Risks and test signals: runtime risk is low because this action only logs. Tests should ensure the annotation binds to the correct feature and that schema selection changes when the layout feature becomes allowed.
