<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/InternalOnly.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/InternalOnly.java

## Purpose

`InternalOnly` is a runtime marker annotation for endpoint classes that depend on internal Recon service components and should not be available as public API surfaces.

## Important APIs and Types

The annotation targets types and is retained at runtime. It requires two attributes: `feature()` and `description()`.

## Control Flow

There is no direct control flow in the annotation. Runtime behavior depends on resource scanners or filters elsewhere that inspect this annotation.

## State and Persistence

No state or persistence exists.

## Dependencies and Integration Points

It integrates with Java reflection, JAX-RS resource registration, and Recon feature/documentation logic that may hide or label internal endpoints.

## Risks and Edge Cases

The annotation itself does not enforce access control. Any endpoint marked `InternalOnly` still needs registration/filter logic to act on it.

## Test Signals

Compilation plus a resource-registration test that verifies annotated classes are treated as internal is the key signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/InternalOnly.java -->
