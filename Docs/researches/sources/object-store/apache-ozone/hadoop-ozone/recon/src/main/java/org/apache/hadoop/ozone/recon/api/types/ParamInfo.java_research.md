# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ParamInfo.java

## Purpose
Mutable cursor/parameter helper for namespace/key insight scans, tracking start prefix, key size threshold, creation date and epoch, replication type, limits, pagination keys, and current count.

## Important APIs, Types, And Functions
declares `ParamInfo`; key fields include `startPrefix`, `keySize`, `creationDate`, `creationDateEpoch`, `replicationType`, `limit`, `prevKey`, `lastKey`, `skipPrevKeyDone`, `currentCount`; important methods include `getStartPrefix`, `getKeySize`, `getCreationDate`, `getCreationDateEpoch`, `getReplicationType`, `getLimit`, `getCurrentCount`, `getPrevKey`, `isSkipPrevKeyDone`, `getLastKey`.

## Control Flow
Constructor converts date strings using `ReconUtils` in the default timezone and stores both text and epoch forms; pagination setters track scan progress.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with plain Java/JDK DTO support. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are timezone-sensitive date parsing, mutable pagination flags, and caller confusion between previous, last, and start prefix cursors.

## Test Signals
Tests should cover date parsing, timezone behavior, invalid dates, limit/current count, and previous/last-key pagination flags.
