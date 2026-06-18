# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/KeyPrefixContainer.java

## Purpose
Public immutable view for key-prefix-to-container indexing, complementing `ContainerKeyPrefix`.

## Important APIs, Types, And Functions
declares `KeyPrefixContainer`.

## Control Flow
Static factories delegate to `ContainerKeyPrefixImpl`; `toContainerKeyPrefix` supports reverse conversion for container-centric index code.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with plain Java/JDK DTO support. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover factory overloads, reverse conversion, and key version preservation.
