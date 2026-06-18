<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/upgrade/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/upgrade/package-info.java

Purpose: Declares the `org.apache.hadoop.ozone.om.response.upgrade` package for upgrade finalization and prepare responses.

Important APIs/types/functions: No executable API. The package groups prepare, cancel-prepare, and finalize-upgrade response classes.

Control flow and persistence: None directly. Concrete classes update `TRANSACTION_INFO_TABLE` or `META_TABLE`, or intentionally perform no response-side DB work.

Dependencies and integration: Integrated by OM upgrade request handling and layout-version management.

Risks and test signals: Documentation-only risk. Concrete tests should cover restart-visible prepare/finalize state and no-op cancel response semantics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/upgrade/package-info.java -->
