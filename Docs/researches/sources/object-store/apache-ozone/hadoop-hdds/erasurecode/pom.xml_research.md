<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/pom.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/pom.xml

## Purpose
This Maven POM defines the `hdds-erasurecode` jar module in Apache Ozone HDDS. It inherits dependency and plugin management from `hdds-hadoop-dependency-client`, declares erasure-code runtime and test dependencies, and applies module-local SpotBugs and compiler configuration.

## Important APIs, Types, And Functions
- Maven coordinates: parent `org.apache.ozone:hdds-hadoop-dependency-client:2.3.0-SNAPSHOT`, artifact `hdds-erasurecode`, packaging `jar`.
- Runtime dependencies include Guava, Hadoop Common, `hdds-common`, and `slf4j-api`.
- Test dependencies include Apache Commons Lang3 and `hdds-config`.
- `spotbugs-maven-plugin` uses `dev-support/findbugsExcludeFile.xml` as the module exclusion filter.
- `maven-compiler-plugin` sets `<proc>none</proc>`, disabling annotation processing for this module build.

## Control Flow
The build starts from the parent POM, resolves dependency versions and plugin defaults from parent management, then builds this module as a jar. SpotBugs applies the module filter file when static analysis runs. Java compilation proceeds without annotation processing, which keeps the erasure-code module independent of annotation processors that may be configured elsewhere in the reactor.

## State And Persistence
The POM persists module metadata, dependency declarations, and build behavior. Build outputs are Maven target artifacts: compiled classes, test classes, reports, and the `hdds-erasurecode` jar. It does not define runtime persistence for Ozone services.

## Dependencies And Integration Points
This module integrates with the HDDS/Ozone Maven reactor through its parent and sibling dependencies. Hadoop Common provides native erasure-code classes used by bridge code such as `HadoopNativeECAccessorUtil`; `hdds-common` supplies Ozone/HDDS annotations and shared client types; SLF4J backs module logging; Guava is used by tests and implementation code such as `CodecRegistry` annotations. The module's service-provider resources participate in `ServiceLoader` discovery at runtime.

## Risks And Edge Cases
The description contains a typo (`Earsurecode`), which is harmless but visible in generated project metadata. Dependency versions are inherited, so parent changes can alter native Hadoop EC compatibility or static-analysis behavior. Disabling annotation processing is intentional but can surprise future code that expects generated sources. The SpotBugs exclusion path is based on `${basedir}`, so moving the filter file or module layout breaks the configured suppression.

## Test Signals
Run `mvn -pl hadoop-hdds/erasurecode test` or the equivalent reactor path to compile the module and execute tests. Static-analysis validation should include the SpotBugs plugin using the module filter. Integration signals include successful `ServiceLoader` registration tests for erasure-code factories and native/non-native coder fallback tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/pom.xml -->
