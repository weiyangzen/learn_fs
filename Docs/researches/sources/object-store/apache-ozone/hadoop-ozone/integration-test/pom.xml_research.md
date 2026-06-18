# sources/object-store/apache-ozone/hadoop-ozone/integration-test/pom.xml

## Purpose

This Maven POM defines the `ozone-integration-test` module under the Apache Ozone parent. It packages the module as a test-support jar and wires the broad dependency surface required by Ozone integration tests: Hadoop clients and test jars, HDDS/Ozone modules and test jars, MiniOzoneCluster, security/Kerberos/KMS/Ranger components, Ratis, RocksDB, filesystem modules, S3 Gateway, CLI tools, and common utility libraries.

## Important Build Elements

- Parent coordinates are `org.apache.ozone:ozone:2.3.0-SNAPSHOT`; artifact is `ozone-integration-test` with jar packaging.
- Most dependencies are `test` scope, reflecting that this module is for integration-test code rather than production runtime code.
- Hadoop dependencies include `hadoop-auth`, `hadoop-common` plus test jar, `hadoop-distcp` plus test jar, HDFS artifacts, KMS artifacts, MapReduce jobclient/core, and MiniKDC.
- Ozone/HDDS dependencies include clients, common/config/container/SCM/server framework modules, admin/client/server interfaces, test utils, manager, mini-cluster, filesystem, CLI, Recon, Freon, S3 Gateway, tools, and RocksDB checkpoint differ.
- Security and ecosystem dependencies include Ranger integration, BouncyCastle, Kerby, Curator, servlet/JAX-RS APIs, Jackson, Guava, Commons libraries, OkHttp, Ratis modules, RocksDB JNI, SLF4J, and reload4j.
- Some Hadoop/KMS/DistCp dependencies exclude reload4j/log4j/SLF4J implementations to keep logging bindings controlled.
- `ozone-s3gateway` is included with a wildcard exclusion of all transitive dependencies, implying this module expects needed transitive dependencies to be supplied explicitly elsewhere.
- Build plugins configure `spotbugs-maven-plugin` to use `dev-support/findbugsExcludeFile.xml` and `maven-compiler-plugin` with annotation processing disabled via `<proc>none</proc>`.

## Control Flow and State Behavior

The POM has no application control flow. During Maven builds it controls dependency resolution, test compilation classpath, static analysis filtering, and compiler behavior. Its state impact is build artifact and classpath composition: integration tests compile against many production and test jars without shipping those dependencies as normal runtime dependencies from this module.

## Dependencies and Integration Points

This file is a central integration point for Ozone integration-test code. It binds the module to the parent build, Maven dependency management, SpotBugs, compiler settings, Hadoop test infrastructure, Ozone MiniOzoneCluster, S3 Gateway classes, security modules, storage backends, Ratis consensus libraries, and filesystem/client APIs.

## Risks and Edge Cases

- The dependency list is intentionally broad; stale or conflicting test-scope dependencies can cause classpath-sensitive integration-test failures.
- Wildcard transitive exclusion on `ozone-s3gateway` makes dependency completeness depend on this POM and parent dependency management.
- Disabling annotation processing avoids unnecessary processors during test compilation, but any future test sources that require generated annotation output would need explicit handling.
- Logging exclusions reduce binding conflicts, but adding new Hadoop/security dependencies can reintroduce duplicate logging implementations.
- Because the module is test-heavy and broad, dependency changes can have a large blast radius across unrelated integration tests.

## Test Signals

The POM's direct signal is successful Maven test compilation and plugin execution for `ozone-integration-test`. It also indirectly enables the Java test bases in this subset by providing Ozone MiniCluster, Ozone client APIs, Hadoop configuration/test utilities, SpotBugs configuration, and related test dependencies.
