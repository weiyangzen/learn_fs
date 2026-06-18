<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ContainerLocationManagerMXBean.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ContainerLocationManagerMXBean.java

Purpose: JMX-facing subset of container location manager reporting.

Important APIs and control flow: exposes `getLocationReport`, returning `StorageLocationReportMXBean[]` and allowing `IOException`.

State and persistence: interface only. It reflects current volume status and does not persist data.

Dependencies and integration: implemented by location/volume managers that publish storage reports through JMX.

Risks and test signals: JMX tests should cover report serialization, failed volume visibility, exception propagation, and compatibility of MXBean-friendly return types.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ContainerLocationManagerMXBean.java -->
