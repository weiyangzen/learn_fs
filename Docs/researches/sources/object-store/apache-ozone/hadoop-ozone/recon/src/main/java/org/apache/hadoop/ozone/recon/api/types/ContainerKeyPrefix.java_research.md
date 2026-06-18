# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ContainerKeyPrefix.java

## Purpose
Public immutable key for Recon container-to-key prefix indexing. It supports container-only, container plus key prefix, and container plus key version forms.

## Important APIs, Types, And Functions
declares `ContainerKeyPrefix`.

## Control Flow
Static factories delegate to the package-private implementation and `toKeyPrefixContainer` lets code convert only when a real key prefix exists.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with plain Java/JDK DTO support. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover factory overloads, conversion to `KeyPrefixContainer`, and container-only use cases.
