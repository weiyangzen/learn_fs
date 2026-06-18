<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/StorageLocationReport.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/StorageLocationReport.java

Purpose: immutable datanode storage/volume usage report with protobuf and JMX representations.

Important APIs and control flow: builder captures ID, failed flag, capacity, SCM-used, remaining, committed, free-space-to-spare, storage type, path, reserved bytes, filesystem capacity, and filesystem available bytes. Getters implement `StorageLocationReportMXBean` and expose additional fields. `getUsableSpace` delegates to `VolumeUsage`. `getProtoBufMessage` serializes full storage reports, while `getMetadataProtoBufMessage` serializes the metadata subset. `getFromProtobuf` rebuilds a report from optional protobuf fields. Static conversion methods map between Hadoop `StorageType` and HDDS protobuf storage type.

State and persistence: immutable after construction. It represents sampled volume state, not long-lived persisted state. Protobuf serialization is used in heartbeat reports.

Dependencies and integration: used by volume reports, node reports, JMX, and SCM heartbeat paths. Depends on Hadoop storage type, protobuf report messages, `VolumeUsage`, and MXBean interface.

Risks and test signals: tests should cover every storage type mapping in both directions, illegal enum values, optional protobuf fields missing, failed-volume string rendering, and `getUsableSpace` with committed/reserved/free-space-to-spare values. Builder does not enforce required fields, so null storage type or location can fail later during serialization or `toString`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/StorageLocationReport.java -->
