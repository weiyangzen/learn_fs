# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/package-info.java

## Purpose
Package-level marker for Recon API type classes under `org.apache.hadoop.ozone.recon.api.types`.

## Important APIs, Types, And Functions
The file only contributes package-level metadata.

## Control Flow
Contains only the package declaration and license header; behavior lives in sibling DTO, enum, and helper classes.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with plain Java/JDK DTO support. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests are not needed for this file directly; package coverage comes from endpoint serialization and DTO tests.
