<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-client/pom.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/interface-client/pom.xml

## Purpose

Builds the hdds-interface-client jar containing generated Java protobuf classes for common HDDS, datanode client, disk balancer, IPC, RPC header, protobuf RPC engine, and reconfigure protocols.

## Important APIs, types, and functions

Artifact: `hdds`. Modules: none in this POM. Key dependencies include `com.google.protobuf:protobuf-java`, `org.apache.ratis:ratis-thirdparty-misc`. Key plugins include `com.salesforce.servicelibs:proto-backwards-compatibility`, `org.apache.maven.plugins:maven-compiler-plugin`, `org.xolstice.maven.plugins:protobuf-maven-plugin`, `org.apache.maven.plugins:maven-antrun-plugin`.

## Control flow

The protobuf-maven-plugin compiles selected proto files, including a custom Ratis generation path for DatanodeClientProtocol. Tests and SpotBugs are skipped because the module contains generated code only.

## State and persistence behavior

The POM persists no runtime state. It controls generated source directories, module membership, dependency resolution, native build outputs under `target`, and test/runtime packaging artifacts.

## Dependencies and integration points

It integrates with the parent Ozone Maven reactor, generated protobuf sources, SpotBugs exclude files, rocksdbjni, CMake/JNI tooling for native builds where enabled, and downstream modules that consume the produced jars or test jars.

## Risks and edge cases

Generated-source modules are sensitive to protoc version, include lists, and package names. Omitting a proto from plugin includes or compatibility checks can silently remove public generated APIs.

## Test signals

Useful signals are a module-level Maven compile, protobuf generation for interface modules, native-profile build on supported Linux agents for rocks-native, and downstream module tests that import generated classes or managed RocksDB wrappers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-client/pom.xml -->
