<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-server/pom.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/interface-server/pom.xml

## Purpose

Builds the hdds-interface-server jar containing generated Java protobuf classes for SCM server-side and inter-SCM protocols. It depends on hdds-interface-client for shared hdds.proto types.

## Important APIs, types, and functions

Artifact: `hdds`. Modules: none in this POM. Key dependencies include `com.google.protobuf:protobuf-java`, `org.apache.ozone:hdds-interface-client`, `org.apache.ratis:ratis-thirdparty-misc`. Key plugins include `com.salesforce.servicelibs:proto-backwards-compatibility`, `org.apache.maven.plugins:maven-compiler-plugin`, `org.xolstice.maven.plugins:protobuf-maven-plugin`, `org.apache.maven.plugins:maven-antrun-plugin`.

## Control flow

The protobuf plugin compiles server protocol files into Java, with compiler annotation processing disabled and tests/SpotBugs skipped because output is generated.

## State and persistence behavior

The POM persists no runtime state. It controls generated source directories, module membership, dependency resolution, native build outputs under `target`, and test/runtime packaging artifacts.

## Dependencies and integration points

It integrates with the parent Ozone Maven reactor, generated protobuf sources, SpotBugs exclude files, rocksdbjni, CMake/JNI tooling for native builds where enabled, and downstream modules that consume the produced jars or test jars.

## Risks and edge cases

Server protocols rely on client common types. Dependency or generation-order errors show up as missing generated classes in SCM/server modules.

## Test signals

Useful signals are a module-level Maven compile, protobuf generation for interface modules, native-profile build on supported Linux agents for rocks-native, and downstream module tests that import generated classes or managed RocksDB wrappers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-server/pom.xml -->
