# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/EntityReadAccessHeatMapResponse.java

## Purpose
Tree node for read-access heatmap responses, containing label/path, size, access count range, color value, and child nodes.

## Important APIs, Types, And Functions
declares `EntityReadAccessHeatMapResponse`; key fields include `label`, `path`, `children`, `size`, `accessCount`, `minAccessCount`, `maxAccessCount`, `color`; important methods include `getLabel`, `getPath`, `getSize`, `getAccessCount`, `getChildren`, `getMinAccessCount`, `getMaxAccessCount`, `getColor`, `equals`, `hashCode`.

## Control Flow
Constructor initializes children to an empty list; equality and hash code compare structural fields so tests can compare expected trees.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson, Jackson inclusion. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover nested tree serialization, min/max/color calculations, and equality with children.
