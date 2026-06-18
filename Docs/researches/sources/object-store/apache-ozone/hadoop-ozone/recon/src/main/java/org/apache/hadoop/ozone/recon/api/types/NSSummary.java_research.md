# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/NSSummary.java

## Purpose
Persisted namespace summary value used by Recon namespace summarization, tracking file counts, logical and replicated sizes, file-size distribution buckets, child directory object IDs, directory name, and parent ID.

## Important APIs, Types, And Functions
declares `NSSummary`; key fields include `numOfFiles`, `sizeOfFiles`, `replicatedSizeOfFiles`, `fileSizeBucket`, `childDir`, `dirName`, `parentId`; important methods include `getNumOfFiles`, `getSizeOfFiles`, `getReplicatedSizeOfFiles`, `getFileSizeBucket`, `getChildDir`, `getDirName`, `addChildDir`, `removeChildDir`, `getParentId`, `toString`.

## Control Flow
Mutable state supports increment/update workflows; child directory set is initialized, add/remove helpers mutate it, and `setDirName` strips trailing slash.

## State And Persistence Behavior
This type is persistence-adjacent: Recon stores or decodes it from OM/Recon metadata representations, so field compatibility and codec/protobuf behavior are part of the durable contract.

## Dependencies And Integration Points
Integrates with plain Java/JDK DTO support. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are mutable persisted summary drift, incorrect file-size bucket lengths, and child directory set updates going out of sync with OM events.

## Test Signals
Tests should cover serialization/deserialization through Recon tables, child directory mutation, file-size bucket length, and trailing slash normalization.
