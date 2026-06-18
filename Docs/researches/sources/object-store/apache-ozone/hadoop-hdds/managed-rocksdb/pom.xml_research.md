<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/pom.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/pom.xml

## Purpose

Builds the hdds-managed-rocksdb jar, a Java wrapper layer around rocksdbjni that adds close tracking, metrics, and safer lifecycle helpers for RocksDB native resources.

## Important APIs, types, and functions

Artifact: `hdds`. Modules: none in this POM. Key dependencies include `com.google.guava:guava`, `commons-io:commons-io`, `jakarta.annotation:jakarta.annotation-api`, `org.apache.hadoop:hadoop-common`, `org.apache.ozone:hdds-common`, `org.apache.ratis:ratis-common`, `org.rocksdb:rocksdbjni`, `org.slf4j:slf4j-api`, `org.apache.commons:commons-lang3`. Key plugins include `org.apache.maven.plugins:maven-compiler-plugin`, `org.apache.maven.plugins:maven-jar-plugin`.

## Control flow

The module compiles Java wrappers and a test jar. It depends on rocksdbjni, hdds-common, Ratis common utilities, Hadoop common, and test-only commons-lang3.

## State and persistence behavior

The POM persists no runtime state. It controls generated source directories, module membership, dependency resolution, native build outputs under `target`, and test/runtime packaging artifacts.

## Dependencies and integration points

It integrates with the parent Ozone Maven reactor, generated protobuf sources, SpotBugs exclude files, rocksdbjni, CMake/JNI tooling for native builds where enabled, and downstream modules that consume the produced jars or test jars.

## Risks and edge cases

Native-resource wrappers need tests on platforms where rocksdbjni loads correctly. Dependency upgrades can change RocksDB ownership semantics and invalidate close-tracking assumptions.

## Test signals

Useful signals are a module-level Maven compile, protobuf generation for interface modules, native-profile build on supported Linux agents for rocks-native, and downstream module tests that import generated classes or managed RocksDB wrappers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/pom.xml -->
