# sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/pom.xml

## Purpose

This Maven module defines Apache Ozone S3 integration tests. It packages test code for S3 Gateway, AWS SDK v1 and v2 coverage, proxy/load-balancing helpers, and mini-cluster S3 scenarios.

## Important APIs, types, and functions

The POM inherits from the `org.apache.ozone:ozone` parent at `2.3.0-SNAPSHOT`, sets artifact ID `ozone-integration-test-s3`, and imports the AWS SDK v2 BOM at `2.46.5`. Dependencies include AWS SDK v1 `aws-java-sdk-core` and `aws-java-sdk-s3`, AWS SDK v2 `s3`, `s3-transfer-manager`, `apache-client`, auth/core/regions/sdk utilities, Jetty server/proxy/client/servlet/util, Ozone client/common/mini-cluster/s3gateway, HDDS server and test utilities, Hadoop common, Ratis common, Guava, commons-io, commons-lang3, Kerby util, JAXB API, servlet API, and SLF4J.

## Control flow, state, and persistence

The POM drives build-time dependency resolution and plugin behavior. The `spotbugs-maven-plugin` points at the module's `dev-support/findbugsExcludeFile.xml`. The compiler plugin disables annotation processing with `<proc>none</proc>`.

## Dependencies and integration points

This module bridges Ozone mini-cluster tests with both AWS SDK generations and Jetty-based proxying. Test dependencies are scoped to avoid exporting the integration harness. The imported SDK v2 BOM keeps v2 AWS artifacts aligned while v1 dependencies are inherited/managed elsewhere by the parent.

## Risks and test signals

Version skew between AWS SDK v1, SDK v2, Jetty, and Ozone S3 Gateway can break compatibility tests. Disabling annotation processing is usually fine for tests but can mask generated-code expectations if new test dependencies require processors. Positive signals are successful compilation of nested SDK v1/v2 suites, SpotBugs using the intended exclusion, and all S3 gateway/proxy tests resolving test-scope dependencies.
