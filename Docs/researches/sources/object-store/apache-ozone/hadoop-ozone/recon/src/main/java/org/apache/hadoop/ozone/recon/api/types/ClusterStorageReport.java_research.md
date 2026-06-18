# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ClusterStorageReport.java

## Purpose
Cluster-wide storage capacity DTO for logical Ozone and underlying filesystem capacity values.

## Important APIs, Types, And Functions
declares `ClusterStorageReport`, `Builder`; key fields include `capacity`, `used`, `remaining`, `committed`, `minimumFreeSpace`, `reserved`, `filesystemCapacity`, `filesystemUsed`, `filesystemAvailable`, `capacity`; important methods include `getCapacity`, `getUsed`, `getRemaining`, `getCommitted`, `getMinimumFreeSpace`, `getReserved`, `getFilesystemCapacity`, `getFilesystemUsed`, `getFilesystemAvailable`, `newBuilder`, `validate`, `build`.

## Control Flow
The builder validates every numeric field is non-negative and logs, rather than rejects, logical inconsistency where used plus remaining exceeds capacity.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with plain Java/JDK DTO support. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are rejecting negative inputs from upstream metric bugs while only warning on used/remaining/capacity inconsistency, which can still expose contradictory API values.

## Test Signals
Tests should cover negative-value exceptions, warning-only inconsistent totals, and JSON/Jackson compatibility with the no-arg constructor.
