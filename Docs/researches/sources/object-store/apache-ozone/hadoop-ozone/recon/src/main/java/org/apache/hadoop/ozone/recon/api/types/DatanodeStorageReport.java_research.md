# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/DatanodeStorageReport.java

## Purpose
Per-datanode storage report mirroring cluster storage metrics plus datanode UUID and hostname.

## Important APIs, Types, And Functions
declares `DatanodeStorageReport`, `Builder`; key fields include `datanodeUuid`, `hostName`, `capacity`, `used`, `remaining`, `committed`, `minimumFreeSpace`, `reserved`, `filesystemCapacity`, `filesystemUsed`; important methods include `getDatanodeUuid`, `getHostName`, `getCapacity`, `getUsed`, `getRemaining`, `getCommitted`, `getMinimumFreeSpace`, `getReserved`, `getFilesystemCapacity`, `getFilesystemUsed`, `getFilesystemAvailable`, `newBuilder`.

## Control Flow
Builder defaults strings to empty, requires hostName non-null, rejects negative metrics, and logs inconsistent used/remaining/capacity totals.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with plain Java/JDK DTO support. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are rejecting negative metrics, allowing warning-only logical inconsistency, and requiring host name while other identity fields may be empty.

## Test Signals
Tests should cover negative validation, host null rejection, warning-only inconsistency, and filesystem metric propagation.
