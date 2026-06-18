<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/upgrade/OMPrepareResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/upgrade/OMPrepareResponse.java

Purpose: Persists the prepare marker transaction index for OM upgrade prepare.

Important APIs/types/functions: Extends `OMClientResponse`. One constructor stores `prepareIndex`; another leaves it at `-1`. `addToDBBatch` writes `TransactionInfo` under `PREPARE_MARKER_KEY` when the index is valid.

Control flow and persistence: For a valid prepare index, writes `TransactionInfo.valueOf(TransactionInfo.DEFAULT_VALUE.getTerm(), prepareIndex)` to `TransactionInfoTable`. Cleanup metadata names `TRANSACTION_INFO_TABLE`.

Dependencies and integration: Used by prepare request handling and upgrade state checks that determine whether OM is in prepared mode.

Risks and test signals: The term is taken from `DEFAULT_VALUE`, so this marker is index-focused. Tests should verify marker write, sentinel no-op, restart detection of prepared state, and cancel-prepare interoperability.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/upgrade/OMPrepareResponse.java -->
