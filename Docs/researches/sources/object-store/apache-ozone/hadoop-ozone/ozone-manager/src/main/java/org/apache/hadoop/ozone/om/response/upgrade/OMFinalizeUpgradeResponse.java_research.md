<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/upgrade/OMFinalizeUpgradeResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/upgrade/OMFinalizeUpgradeResponse.java

Purpose: Persists the finalized OM layout version during upgrade finalization.

Important APIs/types/functions: Extends `OMClientResponse`. Constructor stores `layoutVersionToWrite`; `addToDBBatch` writes it if not `-1`. Uses `LAYOUT_VERSION_KEY` and `META_TABLE`.

Control flow and persistence: On valid version, logs the layout version and batches `MetaTable.put(LAYOUT_VERSION_KEY, String.valueOf(layoutVersionToWrite))`. `-1` is treated as no-op.

Dependencies and integration: Used by finalize-upgrade request handling and OM layout feature finalization.

Risks and test signals: Persisting the wrong layout version can break restart compatibility. Tests should cover valid version write, sentinel no-op, log/state expectations, and replay behavior across OM restart.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/upgrade/OMFinalizeUpgradeResponse.java -->
