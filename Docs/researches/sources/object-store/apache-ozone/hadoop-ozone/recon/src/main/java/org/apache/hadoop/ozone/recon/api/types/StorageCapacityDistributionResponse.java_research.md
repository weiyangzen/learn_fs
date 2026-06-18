# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/StorageCapacityDistributionResponse.java

## Purpose
Composite response for storage utilization distribution, combining global storage, global namespace, used-space breakdown, and per-datanode storage reports.

## Important APIs, Types, And Functions
declares `StorageCapacityDistributionResponse`, `Builder`; key fields include `globalStorage`, `globalNamespace`, `usedSpaceBreakDown`, `dataNodeUsage`, `globalStorage`, `globalNamespace`, `usedSpaceBreakDown`, `dataNodeUsage`; important methods include `getGlobalStorage`, `getGlobalNamespace`, `getUsedSpaceBreakDown`, `getDataNodeUsage`, `newBuilder`, `setGlobalStorage`, `setGlobalNamespace`, `setDataNodeUsage`, `setUsedSpaceBreakDown`, `build`.

## Control Flow
Builder defaults all components to null and simply copies supplied aggregate/list objects into the response.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover complete and partial aggregate responses plus datanode list ordering from the producer.
