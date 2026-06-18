# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/package-info.java

Purpose: documents the `org.apache.hadoop.ozone.container.replication` package as the implementation area for container data replication between datanodes.

Important APIs and types: no executable code is present. The package contains pull and push replication strategies, gRPC transport, source/import abstractions, supervisor scheduling, and metrics.

Control flow and state: none locally.

Dependencies and integration: consumed by Javadoc/package metadata only. It provides context for datanode server-to-server copy infrastructure.

Risks and test signals: no runtime risk. Package declaration should remain aligned with the source tree.
