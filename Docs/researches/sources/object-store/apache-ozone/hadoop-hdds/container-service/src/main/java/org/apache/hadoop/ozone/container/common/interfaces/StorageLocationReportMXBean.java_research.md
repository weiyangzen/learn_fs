<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/StorageLocationReportMXBean.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/StorageLocationReportMXBean.java

Purpose: JMX-safe contract exposing storage location usage fields.

Important APIs and control flow: getters expose storage ID, failed status, capacity, SCM-used bytes, remaining bytes, committed bytes, configured free-space-to-spare, storage location, and storage type name.

State and persistence: interface only. Implemented by immutable `StorageLocationReport`.

Dependencies and integration: used by volume/location managers to expose reports through MXBean APIs without leaking protobuf or Hadoop storage type objects.

Risks and test signals: compatibility tests should ensure implementing classes expose stable getter names and MXBean-compatible return types. Fields beyond this interface, such as reserved and filesystem capacity, are not visible through this MXBean contract.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/StorageLocationReportMXBean.java -->
