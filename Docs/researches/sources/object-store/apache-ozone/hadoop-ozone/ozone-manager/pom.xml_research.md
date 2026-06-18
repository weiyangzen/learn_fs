# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/pom.xml

## Purpose

This Maven POM defines the `ozone-manager` server module, which packages the Apache Ozone Manager service JAR and its runtime/build integrations.

## Important APIs and Types

The artifact is `org.apache.ozone:ozone-manager:2.3.0-SNAPSHOT` with packaging `jar`. It depends on Ozone/HDDS interfaces, server framework, RocksDB integration, Ratis, gRPC/Netty, Hadoop, Jackson, protobuf, Jetty, Reflections, AspectJ, and assorted utilities.

## Control Flow

Build flow includes annotation processing via `maven-compiler-plugin` using `ConfigFileGenerator`, `OmRequestFeatureValidatorProcessor`, and `RegisterValidatorProcessor`. The enforcer plugin overrides root restrictions to allow only selected annotation processors and bans specific imports. The dependency plugin unpacks common static web assets and docs during `prepare-package`. AspectJ compile runs through `aspectj-maven-plugin`. SpotBugs uses the module-local exclude file.

## State and Persistence

The POM controls dependency and build-plugin state, not runtime state. It affects generated config metadata, validators, packaged web resources, and static-analysis behavior.

## Dependencies and Integration Points

Major integrations are HDDS common/client/server/config/interface modules, Ozone common/client/interface/storage modules, RocksDB native/managed components, Ratis common/grpc/netty/server/proto artifacts, gRPC Netty/stub/API, Netty TLS runtime, Hadoop auth/common/HDFS client, Jetty webapp, AspectJ, and SLF4J reload4j runtime. Test dependencies bring in HDDS/Ozone test jars and compile-testing.

## Risks and Edge Cases

The module is central and dependency-heavy; transitive conflicts around Netty, Ratis, RocksDB, Hadoop, and logging are high-impact. Annotation processor configuration is part of source validation and generated config output, so accidental changes can break runtime config metadata. Unpacked web/docs resources make packaging sensitive to upstream artifact contents.

## Test Signals

Signals include full module compile with processors, unit/integration tests, enforcer checks, SpotBugs, AspectJ weaving success, and packaging checks that confirm web assets and docs are included.
