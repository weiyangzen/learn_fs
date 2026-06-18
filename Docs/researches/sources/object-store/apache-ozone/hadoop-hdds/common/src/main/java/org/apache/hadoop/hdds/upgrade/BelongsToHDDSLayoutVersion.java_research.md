# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/upgrade/BelongsToHDDSLayoutVersion.java

## Purpose
Runtime annotation marking a class or field as belonging to a specific HDDS layout feature.

## Important APIs and types
The annotation targets types and fields, is retained at runtime, and has one value of type `HDDSLayoutFeature`.

## Control flow and state
No behavior by itself. Upgrade and layout introspection code can read it via reflection.

## Dependencies and integration points
Used with `HDDSLayoutFeature` to bind code or schema elements to layout versions.

## Risks and test signals
Tests should verify consumers discover the annotation on both classes and fields. Renaming enum values would affect source annotations.
