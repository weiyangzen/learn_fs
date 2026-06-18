# sources/object-store/apache-ozone/hadoop-hdds/docs/pom.xml

## Purpose
This Maven POM defines the `hdds-docs` jar module for Apache Ozone documentation. It packages generated documentation resources rather than compiling application code.

## Important Maven elements
- Parent: `org.apache.ozone:hdds:2.3.0-SNAPSHOT`.
- Artifact: `hdds-docs`, version `2.3.0-SNAPSHOT`, packaging `jar`.
- Properties: `maven.test.skip` is `true` because there is no testable code, and `skipDocs` defaults to `false`.
- `maven-compiler-plugin` sets `<proc>none</proc>` to disable annotation processing.
- `exec-maven-plugin` binds goal `exec` to the `compile` phase and executes `../../hadoop-ozone/dev-support/checks/docs.sh`, controlled by `<skip>${skipDocs}</skip>`.

## Control flow
During Maven `compile`, the exec plugin invokes the docs check/generation script unless `skipDocs` is true. The resulting generated resources are expected to land under the module target tree and be packaged into the jar. Tests are skipped for this module.

## State and persistence
The POM itself has no runtime state. Build outputs persist under `docs/target`, especially generated docs resources that can be included in the jar artifact.

## Dependencies and integration points
This module depends on the parent HDDS Maven configuration for plugin versions and properties. It integrates with the external script `hadoop-ozone/dev-support/checks/docs.sh`, which in turn is expected to drive Hugo generation through `docs/dev-support/bin/generate-site.sh`.

## Risks and edge cases
- The executable path is relative to this module and crosses into `hadoop-ozone`; repository layout changes can break the build.
- Since tests are skipped, regressions in docs generation are only caught by script exit status and artifact inspection.
- `skipDocs` can disable the main behavior, so release/CI profiles need to ensure it is not accidentally true where documentation artifacts are required.
- Disabling annotation processing is appropriate for a docs module but can hide accidental introduction of Java sources that expect processors.

## Test signals
Run `mvn compile` for the docs module with `skipDocs=false` and confirm `docs.sh` executes and generated docs are packaged. Run with `-DskipDocs=true` to confirm skip behavior. Check effective POM/plugin versions from the parent if plugin behavior changes.
