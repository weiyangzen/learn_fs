<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/pom.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/rocks-native/pom.xml

## Purpose

Builds the hdds-rocks-native module, which provides JNI wrappers and optional native build support for RocksDB raw SST tooling.

## Important APIs, types, and functions

Artifact: `hdds`. Modules: none in this POM. Key dependencies include `com.google.guava:guava`, `commons-io:commons-io`, `org.apache.commons:commons-lang3`, `org.apache.ozone:hdds-common`, `org.apache.ozone:hdds-managed-rocksdb`, `org.rocksdb:rocksdbjni`, `org.slf4j:slf4j-api`, `org.apache.ozone:hdds-test-utils`. Key plugins include `com.github.spotbugs:spotbugs-maven-plugin`, `org.apache.maven.plugins:maven-compiler-plugin`, `org.codehaus.mojo:build-helper-maven-plugin`, `org.codehaus.mojo:exec-maven-plugin`, `org.codehaus.mojo:properties-maven-plugin`, `org.apache.maven.plugins:maven-dependency-plugin`, `com.googlecode.maven-download-plugin:download-maven-plugin`, `org.apache.maven.plugins:maven-patch-plugin`, `org.apache.maven.plugins:maven-antrun-plugin`, `org.apache.maven.plugins:maven-compiler-plugin`.

## Control flow

The normal build compiles Java. The rocks_tools_native profile writes the RocksDB JNI library name, unpacks/downloads RocksDB artifacts, applies a patch, generates JNI headers, runs CMake, links ozone_rocksdb_tools, and packages native resources.

## State and persistence behavior

The POM persists no runtime state. It controls generated source directories, module membership, dependency resolution, native build outputs under `target`, and test/runtime packaging artifacts.

## Dependencies and integration points

It integrates with the parent Ozone Maven reactor, generated protobuf sources, SpotBugs exclude files, rocksdbjni, CMake/JNI tooling for native builds where enabled, and downstream modules that consume the produced jars or test jars.

## Risks and edge cases

The native profile is platform and toolchain sensitive. CMake variables, RocksDB version, ABI flags, JNI headers, and bundled dependent libraries must stay aligned with rocksdbjni.

## Test signals

Useful signals are a module-level Maven compile, protobuf generation for interface modules, native-profile build on supported Linux agents for rocks-native, and downstream module tests that import generated classes or managed RocksDB wrappers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/pom.xml -->
