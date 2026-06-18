# sources/storage-engines/foundationdb/bindings/java/pom.xml.in

## Purpose
`pom.xml.in` is a Maven POM template for publishing/building the FoundationDB Java binding artifact. Placeholder tokens `NAME` and `VERSION` are intended to be substituted by the build system.

## Important APIs, Types, and Functions
The template declares Maven coordinates `org.foundationdb:NAME:VERSION`, `jar` packaging, project name `foundationdb-java`, project metadata, organization/developer entries, SCM URL, and Apache 2.0 license metadata.

## Control Flow
There is no executable control flow. The build system expands the template into a real `pom.xml`, and Maven consumes the resulting metadata during packaging, installation, or publication.

## State and Persistence Behavior
The file persists artifact identity and publication metadata. It does not declare dependencies, plugins, source/target levels, or test configuration, so those are expected to be supplied elsewhere in the build.

## Dependencies and Integration Points
It integrates with Maven's POM 4.0.0 model and the FoundationDB release/build process. The description explicitly points users to FoundationDB client releases because the Java binding requires the native client library under a different license.

## Risks and Edge Cases
Publishing correctness depends on token substitution. If `NAME` or `VERSION` are not replaced, invalid or misleading artifact coordinates can be published. Because dependency and plugin declarations are absent, consumers cannot infer the native client dependency from Maven metadata alone.

## Test Signals
Signals are build-time: generated POM validation, Maven package/install/deploy success, and artifact metadata inspection after substitution.
