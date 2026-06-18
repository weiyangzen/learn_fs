# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/MissingContainerMetadata.java

## Purpose
Metadata for a missing container, including missing-since timestamp, key count, pipeline UUID, and historical replica locations.

## Important APIs, Types, And Functions
declares `MissingContainerMetadata`; key fields include `containerID`, `missingSince`, `keys`, `pipelineID`, `replicas`; important methods include `getContainerID`, `getKeys`, `getReplicas`, `getMissingSince`, `getPipelineID`.

## Control Flow
Constructed from unhealthy-container table records plus `ContainerHistory` rows; JAXB annotations preserve XML field names.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with JAXB/XML, SCM pipeline metadata. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover conversion from missing-container records and replica history output.
