# sources/object-store/apache-ozone/hadoop-ozone/iceberg/pom.xml

## Purpose
This Maven POM defines the `ozone-iceberg` module, which packages Apache Ozone integration utilities for Iceberg tables.

## Important APIs, types, and functions
The module inherits from the Ozone parent, packages a jar, and overrides `maven.compiler.release` to 11 because Iceberg 1.10+ uses Java 11 bytecode. Dependencies include Picocli, Avro, Hadoop common, Iceberg API/core/ORC/Parquet, Ozone CLI/common/filesystem artifacts, Parquet column, SLF4J, Hadoop MapReduce runtime, and reload4j runtime.

## Control flow
Build-time behavior disables annotation processing with `maven-compiler-plugin` and configures SpotBugs with the module exclude filter, forked execution, and 2048 MB heap.

## State and persistence behavior
The POM is build metadata. It does not store runtime state.

## Dependencies and integration points
The dependency set supports `IcebergCommand`, `RewriteTablePathCommand`, metadata rewriting, manifest IO, position-delete readers/writers, and Ozone filesystem access at runtime.

## Risks and edge cases
The POM contains many exclusions to avoid dependency conflicts, especially HTTP client, checker, roaring bitmap, Jersey, JAXB, YARN, Avro duplication, and Jetty websocket artifacts. Version drift with Iceberg, Avro, ORC, Parquet, or Hadoop can break binary compatibility.

## Test signals
Module compilation and `TestRewriteTablePathOzoneAction` are the primary signals. SpotBugs uses the empty exclude file.
