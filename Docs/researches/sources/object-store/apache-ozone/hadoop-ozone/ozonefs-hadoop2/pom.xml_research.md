<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/pom.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/pom.xml

## Purpose
Maven module for Hadoop 2-compatible Ozone filesystem distribution.

## Important APIs, types, and functions
Builds artifact `ozone-filesystem-hadoop2`. Dependencies include Hadoop 2 `hadoop-common` as provided, `hadoop-hdfs-client`, `ozone-filesystem-shaded`, Ratis thirdparty misc, SLF4J, reload4j, and Ozone test-jar. Plugins compile generated sources, unpack the shaded filesystem jar into classes, run SpotBugs, copy source files into generated sources, and replace unshaded protobuf references.

## Control flow
During `generate-sources`, antrun copies `src/main/java` to `target/generated-sources/java`. During `process-sources`, replacer rewrites `com.google.protobuf` references to the Ozone shaded prefix. During `prepare-package`, the dependency plugin unpacks `ozone-filesystem-shaded`.

## State and persistence behavior
Build output is generated under `target/`; no runtime state is defined.

## Dependencies and integration points
This module packages compatibility classes that omit Hadoop 3 APIs and supplies Hadoop 2 RPC transport. It depends on the shaded common filesystem payload while avoiding conflicts with Hadoop-provided dependencies.

## Risks and test signals
Build risks include source-rewrite drift, shading mismatches, and dependency conflicts with Hadoop 2 classpaths. Signals are Maven compile/package, SpotBugs scoped to `org.apache.hadoop.fs.ozone.*`, and the Hadoop 2-specific `TestOmKeyInfoWithHadoop2`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/pom.xml -->
