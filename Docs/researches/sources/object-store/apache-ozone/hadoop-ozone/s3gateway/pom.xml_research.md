# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/pom.xml

Purpose: this Maven POM builds the `ozone-s3gateway` jar, defining the server, REST/JAX-RS, XML binding, Ozone client, security, tracing, and runtime container dependencies required for the S3-compatible gateway.

Important APIs and flow: it inherits from the root `org.apache.ozone:ozone` parent at version `2.3.0-SNAPSHOT`, disables annotation processing for compilation, and declares runtime Jersey, HK2, Weld, JAXB, Jetty, Netty, and reload4j dependencies. It also depends on Ozone client/common/interface modules, HDDS framework modules, Hadoop auth/common, Jackson XML/JAXB support, servlet/CDI/inject APIs, OpenTelemetry API, Ratis, picocli, commons libraries, and an `ozone-client` test jar.

State, dependencies, risks, and tests: the build persists compiled classes and unpacks static web assets/docs during `prepare-package` from `hdds-server-framework` and `hdds-docs`. SpotBugs uses `dev-support/findbugsExcludeFile.xml`. Risks include mixed `jakarta.*` and `javax.*` API dependencies, runtime-only CDI/Jersey binding mismatches, and security-sensitive dependency drift. Test signals are Maven compile/test, classpath generation, SpotBugs loading, and packaging verifying the static web assets and servlet runtime are assembled.
