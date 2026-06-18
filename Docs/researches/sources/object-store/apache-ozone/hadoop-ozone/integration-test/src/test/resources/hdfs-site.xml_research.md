# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/resources/hdfs-site.xml

Purpose: This placeholder `hdfs-site.xml` exists on the integration-test classpath for Hadoop configuration compatibility.

Important APIs and types: It is an XML `<configuration>` with no properties.

Control flow: There is no executable flow.

State and persistence behavior: It is static and empty; no runtime state is persisted.

Dependencies and integration points: Some Hadoop components expect `hdfs-site.xml` to be present even when tests are not configuring HDFS-specific settings. This file supplies an empty override layer.

Risks: Because it contains no properties, any test requiring HDFS-specific configuration must set it elsewhere. Accidental assumptions that this file configures HDFS behavior would be incorrect.

Test signals: None directly, other than successful resource loading without HDFS overrides.
