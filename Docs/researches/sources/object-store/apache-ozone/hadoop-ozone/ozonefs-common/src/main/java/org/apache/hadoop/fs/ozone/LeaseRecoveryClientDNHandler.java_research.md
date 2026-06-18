<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/LeaseRecoveryClientDNHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/LeaseRecoveryClientDNHandler.java

## Purpose
Client-side lease recovery helper that contacts datanodes through the adapter to determine actual block lengths before committing OM recovery metadata.

## Important APIs, types, and functions
The static `getOmKeyLocationInfos` method accepts `LeaseKeyInfo`, `OzoneClientAdapter`, and a force-recovery flag. It compares finalized key locations with open-key locations, calls `adapter.finalizeBlock`, updates block lengths, and returns the recovered location list.

## Control flow
The method handles three cases: open file table has an extra final block, open penultimate block length differs from file table final block with matching local ID, or open and closed tables have the same block count. On datanode `NO_SUCH_BLOCK` or `CONTAINER_NOT_FOUND`, it retries the file-table final block when that aligns with the open penultimate block. Other failures are thrown unless force recovery is enabled.

## State and persistence behavior
The method mutates `OmKeyLocationInfo` lengths in memory and may append an open final block to the file-table list. Durable recovery occurs later when filesystem code builds `OmKeyArgs` and calls `adapter.recoverFile`.

## Dependencies and integration points
Used by Hadoop 3/main and rooted lease recovery implementations. It depends on OM lease metadata, HDDS `StorageContainerException` result codes, datanode block finalization via `OzoneClientAdapter`, and `FORCE_LEASE_RECOVERY_ENV`.

## Risks and test signals
The logic is sensitive to block list ordering and local ID comparisons. Incorrect fallback can commit wrong file length or skip a valid final block. Tests should cover one-block files, extra open final blocks, mismatched penultimate lengths, missing containers, no-such-block, and forced vs strict recovery.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/LeaseRecoveryClientDNHandler.java -->
