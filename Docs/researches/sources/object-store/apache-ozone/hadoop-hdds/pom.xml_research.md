<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/pom.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/pom.xml

## Purpose

Aggregator POM for the HDDS subproject. It lists all HDDS modules, creates a test jar, configures remote ASF resources, and defines a parallel-tests profile that controls surefire fork directories and shared test paths.

## Important APIs, types, and functions

Artifact: `ozone-main`. Modules: `annotations`, `cli-common`, `client`, `common`, `config`, `container-service`, `crypto-api`, `crypto-default`, `docs`, `erasurecode`, `framework`, `hadoop-dependency-client`, `interface-admin`, `interface-client`, `interface-server`, `managed-rocksdb`, `rocks-native`, `rocksdb-checkpoint-differ`, `server-scm`, `test-utils`. Key dependencies include `org.apache.ozone:ozone-dev-support`. Key plugins include `org.apache.maven.plugins:maven-jar-plugin`, `org.apache.maven.plugins:maven-remote-resources-plugin`, `org.apache.hadoop:hadoop-maven-plugins`, `org.apache.maven.plugins:maven-surefire-plugin`.

## Control flow

Maven enters this POM from the parent ozone-main build, then builds the listed modules in dependency order. Profiles add test fork isolation and shared coordination directories for concurrent JUnit execution.

## State and persistence behavior

The POM persists no runtime state. It controls generated source directories, module membership, dependency resolution, native build outputs under `target`, and test/runtime packaging artifacts.

## Dependencies and integration points

It integrates with the parent Ozone Maven reactor, generated protobuf sources, SpotBugs exclude files, rocksdbjni, CMake/JNI tooling for native builds where enabled, and downstream modules that consume the produced jars or test jars.

## Risks and edge cases

Module ordering and profile properties affect the whole HDDS reactor. Changes can break downstream module builds, test isolation, or source-release resource processing.

## Test signals

Useful signals are a module-level Maven compile, protobuf generation for interface modules, native-profile build on supported Linux agents for rocks-native, and downstream module tests that import generated classes or managed RocksDB wrappers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/pom.xml -->
