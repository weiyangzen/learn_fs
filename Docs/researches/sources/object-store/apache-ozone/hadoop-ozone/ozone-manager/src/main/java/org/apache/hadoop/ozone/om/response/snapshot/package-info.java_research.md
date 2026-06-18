<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/package-info.java

Purpose: Declares the `org.apache.hadoop.ozone.om.response.snapshot` package for OM snapshot response classes.

Important APIs/types/functions: No executable API. The package groups create, delete, purge, rename, set-property, and snapshot key/table movement responses.

Control flow and persistence: None directly. Concrete classes update active OM snapshot info plus snapshot checkpoint RocksDB stores, local data, cache mappings, and checkpoint directories.

Dependencies and integration: Integrated by snapshot request handling, snapshot background services, snapshot chain management, and SnapDiff support.

Risks and test signals: Documentation-only risk. Concrete tests should emphasize multi-store atomicity, snapshot locks, and checkpoint filesystem side effects.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/package-info.java -->
