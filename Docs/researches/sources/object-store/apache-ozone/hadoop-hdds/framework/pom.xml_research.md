<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/pom.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/pom.xml

## Purpose
This Maven POM defines the `hdds-server-framework` jar module, its dependencies, annotation processing, static-analysis filters, and test-jar generation.

## Important APIs, Types, and Functions
Key metadata includes parent `org.apache.ozone:hdds:2.3.0-SNAPSHOT`, artifact `hdds-server-framework`, packaging `jar`, and property `classpath.skip=false`. Dependencies span logging, Jackson, Hadoop common/auth, Ozone HDDS modules, Ratis APIs, Jetty/Jersey, RocksDB, metrics, OpenTelemetry, BouncyCastle, YAML, and test dependencies. Plugins configure SpotBugs exclusions, compiler annotation processors `ConfigFileGenerator` and `ReplicateAnnotationProcessor`, Maven enforcer import restrictions, and test-jar creation.

## Control Flow
Build flow resolves dependencies, runs annotation processors with `-AartifactId`, applies SpotBugs exclude filter, enforces banned imports, compiles framework code, and attaches a test jar.

## State and Persistence Behavior
The POM is persistent build state. Generated config metadata and replicated annotations are build outputs, not checked here.

## Dependencies and Integration Points
It integrates the framework module into the parent HDDS reactor and supplies dependencies needed by config classes, HTTP servlets, Ratis configuration, security, metrics, and tests.

## Risks and Test Signals
Risks include dependency scope drift, annotation processor misconfiguration, SpotBugs filter path breakage, and runtime/provided logging conflicts. Test signals are `mvn -pl hadoop-hdds/framework test`, annotation-generated config files, SpotBugs, enforcer checks, and test-jar consumers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/pom.xml -->
