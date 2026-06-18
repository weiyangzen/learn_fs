# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ContainerMetadata.java

## Purpose
Container inventory row for container list APIs, exposing container id, number of keys, and SCM pipeline objects.

## Important APIs, Types, And Functions
declares `ContainerMetadata`; key fields include `containerID`, `numberOfKeys`, `pipelines`; important methods include `getContainerID`, `setContainerID`, `getNumberOfKeys`, `setNumberOfKeys`, `getPipelines`, `setPipelines`.

## Control Flow
Constructed with a container id and then filled by setters; JAXB annotations retain XML field names while Jackson exposes pipelines.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson, JAXB/XML, SCM pipeline metadata. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should assert XML/Jackson names and behavior when pipelines are absent.
