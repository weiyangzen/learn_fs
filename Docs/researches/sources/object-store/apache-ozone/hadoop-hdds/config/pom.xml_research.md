# sources/object-store/apache-ozone/hadoop-hdds/config/pom.xml

## Purpose
Maven module descriptor for `hdds-config`, the lightweight jar containing Ozone configuration annotations, reflection utilities, parsers, and the annotation processor.

## Important APIs, Types, And Functions
Declares parent `hdds`, artifact `hdds-config`, jar packaging, dependencies on `hadoop-common` with broad exclusions and `slf4j-api`, plus test Guava. Build plugins configure compiler and test jar generation.

## Control Flow
Main compile disables annotation processing with `<proc>none>` so the module can compile its own processor without recursive execution. Test compile enables `ConfigFileGenerator` from the built `hdds-config` artifact and passes an empty `artifactId` processor option.

## State And Persistence
No runtime state. Build outputs include the main jar, test jar, and generated test compile resources such as `ozone-default-generated.xml`.

## Dependencies And Integration Points
Feeds every module that uses `@Config` and the annotation processor. The test jar exposes test configuration examples to downstream tests.

## Risks
The broad Hadoop dependency exclusion keeps the module small but can hide transitive assumptions. Processor configuration must remain synchronized with `ConfigFileGenerator` options and artifact version properties.

## Test Signals
Signals include `mvn -pl hadoop-hdds/config test`, generated default XML during test compile, and consumers resolving both main and test jars without unexpected transitive dependency expansion.
