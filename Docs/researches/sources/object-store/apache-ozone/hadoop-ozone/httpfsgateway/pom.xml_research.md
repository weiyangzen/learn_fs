# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/pom.xml

## Purpose
This Maven POM defines the `ozone-httpfsgateway` module, its dependencies, resource filtering, test configuration, site generation, SpotBugs filter, and optional distribution packaging profile.

## Important APIs, Types, and Functions
The artifact is `org.apache.ozone:ozone-httpfsgateway:2.3.0-SNAPSHOT` with `jar` packaging. Dependencies include reload4j, Jackson, json-simple, JAX-RS, servlet API, Hadoop auth/common/HDFS client, HDDS/Ozone modules, Jetty, Jersey/HK2, JAXB, Ozone filesystem runtime, Curator, and SLF4J bindings. Build plugins configure checkstyle, compiler annotation processing disabled via `<proc>none</proc>`, surefire timeout/listener behavior, Javadoc grouping, Ant resource copy/site XSLT tasks, and SpotBugs exclusions.

## Control Flow
At build time, filtered resources process `httpfs.properties`, unfiltered resources copy everything else, test resources are included both filtered and unfiltered, and Ant tasks create test webapp resources and site HTML from `httpfs-default.xml`. The `dist` profile uses `maven-assembly-plugin` with Hadoop's `hadoop-httpfs-dist` descriptor.

## State and Persistence Behavior
The POM does not manage runtime state. It controls generated build outputs, filtered metadata, test-class webapp resources, and optional assembly artifacts.

## Dependencies and Integration Points
The module is tied to the parent Ozone build and depends on local Ozone/HDDS artifacts. Runtime dependencies wire the gateway to Jetty/Jersey, Hadoop authentication, Hadoop filesystem APIs, and the Ozone filesystem implementation.

## Risks and Edge Cases
The module has both `javax.servlet` and `jakarta.ws.rs` APIs, so dependency alignment matters. The test resource section includes the same directory twice with different filtering settings, which can be surprising. The empty SpotBugs filter means current warnings are not suppressed. Runtime scope for many server dependencies assumes the assembly/runtime classpath is assembled correctly.

## Test Signals
Surefire is configured with single thread count, a timeout listener, and 600-second fork timeout. This subset includes no HttpFS gateway test classes, but the module has `TestHttpFSMetrics` outside the assigned list.
