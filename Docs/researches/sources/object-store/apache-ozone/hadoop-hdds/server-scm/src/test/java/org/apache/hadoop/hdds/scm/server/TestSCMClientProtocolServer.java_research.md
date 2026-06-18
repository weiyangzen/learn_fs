# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/server/TestSCMClientProtocolServer.java

## Purpose
`TestSCMClientProtocolServer` validates selected SCM client protocol behavior: SCM decommission error handling, read-only admin authorization, container listing compatibility, container count lookup, and pagination ordering without duplicates.

## Important APIs, Types, and Functions
- `SCMClientProtocolServer.listContainer`, `getContainerCount`, and access through `StorageContainerLocationProtocolServerSideTranslatorPB.decommissionScm` are tested.
- `StorageContainerManager.checkAdminAccess` is exercised through the real SCM instance.
- Helpers `mockStorageContainerManager`, `newContainerWithLastUsedTime`, and `newContainerInfoForTest` provide container-manager stubs.

## Control Flow
Setup starts a real test SCM with read-only administrator config and exits safe mode. Decommission test calls the translator with the current SCM ID and asserts the response contains "Cannot remove current leader." Admin test creates a UGI for the read-only admin and verifies read access succeeds but write access throws. Listing/count tests use a standalone `SCMClientProtocolServer` with mocked SCM/container manager. Pagination test creates out-of-order container IDs with increasing last-used times and repeatedly calls `listContainer` using the last returned ID plus one as the next start.

## State and Persistence Behavior
The real SCM setup uses temp metadata and is stopped after tests. Mocked container listing state is in-memory. Pagination behavior depends on sorted container ID output, not insertion order.

## Dependencies and Integration Points
The class integrates client protocol server, protobuf translator, SCM HA context, admin ACL configuration, UGI, reconfiguration handler, container manager, and legacy list-container API accepting replication factor.

## Risks and Edge Cases
Covered risks include attempting to decommission the current leader, read-only admin incorrectly receiving write authority, legacy list-container compatibility, count lookup by lifecycle state, and duplicate/skip bugs in ID-based pagination. It does not test remote authorization contexts or multiple SCM peers.

## Test Signals
The pagination test is a strong regression signal: expected IDs `[5, 10, 100]` and uniqueness ensure `listContainer` sorts and advances by container ID correctly.
