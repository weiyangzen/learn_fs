# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/DatanodeMetadata.java

## Purpose
Detailed datanode row for Recon datanode APIs, combining SCM node state, operational state, heartbeat, storage report, pipeline membership, container counts, version, layout, and network location.

## Important APIs, Types, And Functions
declares `DatanodeMetadata`, `Builder`; key fields include `uuid`, `hostname`, `state`, `opState`, `lastHeartbeat`, `datanodeStorageReport`, `pipelines`, `containers`, `openContainers`, `leaderCount`; important methods include `getHostname`, `getState`, `getOperationalState`, `getLastHeartbeat`, `getDatanodeStorageReport`, `getPipelines`, `getContainers`, `getOpenContainers`, `getLeaderCount`, `getUuid`, `getVersion`, `getSetupTime`.

## Control Flow
`Builder.setDatanode` extracts identity and version fields from `DatanodeInfo`; `build` requires hostname, state, last heartbeat, and storage report.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson inclusion, JAXB/XML, SCM datanode metadata, SCM pipeline metadata. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are required builder fields not being set, optional fields disappearing from JSON due to inclusion rules, and SCM state/version fields drifting from `DatanodeInfo` semantics.

## Test Signals
Tests should cover required-field null checks, `setDatanode` mapping, optional JSON omission, and stale heartbeat/state rendering.
