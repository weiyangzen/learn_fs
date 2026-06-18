# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/KeyInsightInfoResponse.java

## Purpose
Paged response for key insight APIs covering open/deleted/repeated/non-FSO/FSO key collections and aggregate replicated/unreplicated sizes.

## Important APIs, Types, And Functions
declares `KeyInsightInfoResponse`; key fields include `lastKey`, `replicatedDataSize`, `unreplicatedDataSize`, `nonFSOKeyInfoList`, `fsoKeyInfoList`, `repeatedOmKeyInfoList`, `deletedDirInfoList`, `responseCode`; important methods include `getLastKey`, `getReplicatedDataSize`, `getUnreplicatedDataSize`, `getNonFSOKeyInfoList`, `getFsoKeyInfoList`, `getRepeatedOmKeyInfoList`, `getDeletedDirInfoList`, `getResponseCode`.

## Control Flow
Constructor initializes all row lists and status OK; services fill the relevant list and `lastKey` for pagination.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson, Jackson inclusion. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover each list type, aggregate sizes, pagination cursor, and non-empty JSON inclusion.
