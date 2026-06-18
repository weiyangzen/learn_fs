<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tenant/OMSetRangerServiceVersionResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tenant/OMSetRangerServiceVersionResponse.java

Purpose: Persists the Ranger service version string used by S3 tenant/Ranger synchronization state.

Important APIs/types/functions: Extends `OMClientResponse`. The success constructor stores a metadata table key and version string. The failure constructor calls `checkStatusNotOK()`. `addToDBBatch` writes the string to `MetaTable`; `getNewServiceVersion` is test-visible.

Control flow and persistence: A successful request performs one `putWithBatch(batchOperation, serviceVersionKey, serviceVersionValueStr)` on `META_TABLE`. There is no explicit status check inside `addToDBBatch`; correctness depends on the response lifecycle invoking it only for successful responses.

Dependencies and integration: Used by OM tenant/Ranger service version update request handling and likely consumed by background Ranger sync logic.

Risks and test signals: Wrong key or stale version can desynchronize Ranger policy state. Tests should cover successful meta-table write, failure no-op through `checkStatusNotOK`, and accessor returning the stored version.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tenant/OMSetRangerServiceVersionResponse.java -->
