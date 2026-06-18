# sources/object-store/apache-ozone/hadoop-ozone/vapor/pom.xml

## Purpose
Maven module descriptor for `ozone-vapor`, server-side load and simulation tools built on Freon/Ozone internals.

## Important APIs, types, and functions
Defines artifact `org.apache.ozone:ozone-vapor`, dependencies on Jackson, protobuf, metrics, Hadoop common/HDFS, HTTP components, HDDS client/server/container/SCM modules, Ozone admin/common/freon/manager/interface storage, Ratis client/common/proto, picocli, and MetaInfServices. Build config mirrors tools module with SpotBugs, annotation processors, and enforcer import bans.

## Control flow
Compile runs service-registration and picocli native-image processors. SpotBugs reads the empty module filter. Enforcer restricts selected annotation imports.

## State and persistence behavior
No runtime state, but dependency graph enables Vapor commands that talk to SCM, datanodes, containers, and Ratis and may write local load-test data.

## Dependencies and integration points
This module intentionally integrates deeply with server internals rather than only public clients.

## Risks and edge cases
Broad internal dependencies increase coupling to implementation changes. Runtime tools can stress real clusters, so classpath and version alignment matter.

## Test signals
Build success, service-loader registration of `VaporSubcommand` implementations, and static-analysis success.
