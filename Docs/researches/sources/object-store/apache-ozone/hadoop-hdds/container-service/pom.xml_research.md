# sources/object-store/apache-ozone/hadoop-hdds/container-service/pom.xml

## Purpose
Maven descriptor for `hdds-container-service`, the datanode/container runtime module.

## Important APIs, Types, And Functions
Declares dependencies on Jackson, Guava, protobuf, Hadoop auth/common/HDFS, HDDS common/client/config/framework/interface modules, Ratis client/server/grpc/netty/proto, RocksDB JNI, Netty, OpenTelemetry, SnakeYAML, docs, runtime zstd/log4j extras/JAXB/HDFS client, and test jars/utilities.

## Control Flow
Build config wires SpotBugs with the module exclusion file, enables `ConfigFileGenerator` as the selected annotation processor, overrides the root enforcer annotation ban for selected processors, and unpacks shared web static assets and docs into the datanode webapp during prepare-package.

## State And Persistence
Build outputs include the container-service jar, generated config metadata, webapp static/docs resources, and test classpath artifacts.

## Dependencies And Integration Points
This module integrates datanode service startup, container RPC handling, Ratis replication, RocksDB metadata, web UI endpoints, metrics, security, and configuration generation.

## Risks
Dependency breadth increases classpath and shading/version risks. Annotation processor selection must stay aligned with banned-import rules. Web asset unpacking couples package output to `hdds-server-framework` and `hdds-docs` artifacts.

## Test Signals
Signals include full module compile/test, annotation-generated default XML, SpotBugs load of the empty filter, enforcer success, and packaged webapp resources.
