<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/upgrade/OMCancelPrepareResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/upgrade/OMCancelPrepareResponse.java

Purpose: Response object for cancel-prepare upgrade requests.

Important APIs/types/functions: Extends `OMClientResponse`. Constructor accepts `OMResponse`. `addToDBBatch` is overridden as an intentional no-op. Cleanup metadata names `TRANSACTION_INFO_TABLE`.

Control flow and persistence: The comment explains that cancel prepare deletes the prepare marker file and updates in-memory state outside this response, so no DB/cache update is needed here.

Dependencies and integration: Used by upgrade prepare cancellation flow. It relies on request-side or manager-side logic for marker-file deletion and state transition.

Risks and test signals: Risk is assuming DB mutation happens here when it does not. Tests should verify cancel prepare removes marker/in-memory state through the owning request path and that response replay does not change transaction info.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/upgrade/OMCancelPrepareResponse.java -->
