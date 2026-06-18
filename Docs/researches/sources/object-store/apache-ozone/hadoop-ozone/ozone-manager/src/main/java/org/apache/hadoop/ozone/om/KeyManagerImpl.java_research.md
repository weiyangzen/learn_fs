# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/KeyManagerImpl.java

## Purpose
`KeyManagerImpl` is the main `KeyManager` implementation used by Ozone Manager for key and filesystem metadata reads, key listing, multipart upload listing, ACL checks, deletion work discovery, block-location refresh, and lifecycle management of key-related background services. It bridges OM metadata tables, SCM container/pipeline APIs, block token generation, KMS file encryption metadata, snapshot maintenance services, and FS-optimized bucket semantics.

## Important APIs, types, and functions
The class implements `KeyManager` and depends heavily on `OzoneManager`, `ScmClient`, `OMMetadataManager`, `OzoneBlockTokenSecretManager`, `KeyProviderCryptoExtension`, and `OMPerformanceMetrics`. Constructors wire OM dependencies, SCM block size, block token enablement, metadata manager, KMS provider, secret manager, and performance metrics.

Lifecycle methods are `start(OzoneConfiguration)` and `stop()`. `start` conditionally starts `CompactionService`, `KeyDeletingService`, `DirectoryDeletingService`, `OpenKeyCleanupService`, `SstFilteringService`, `SnapshotDefragService`, `SnapshotDeletingService`, `MultipartUploadCleanupService`, and the DNS-to-switch mapper used for datanode sorting. The snapshot SST filtering path intentionally yields to snapshot defrag if both intervals are enabled.

Read APIs include `lookupKey`, `getKeyInfo`, `getObjectTagging`, `lookupFile`, `getFileStatus`, and `listStatus`. Listing and maintenance APIs include `listKeys`, `listMultipartUploads`, `listParts`, `getPendingDeletionKeys`, `getDeletedKeyEntries`, `getRenamesKeyEntries`, `getDeletedDirEntries`, `getPendingDeletionSubDirs`, `getPendingDeletionSubFiles`, `getExpiredOpenKeys`, and `getExpiredMultipartUploads`. ACL APIs are `getAcl` and `checkAccess`.

Key helper methods are `readKeyInfo`, `getOmKeyInfo`, `getOmKeyInfoFSO`, `createFakeDirIfShould`, `createDirectoryKey`, `getFileEncryptionInfo`, `addBlockToken4Read`, `refreshPipeline`, `refreshPipelineFromCache`, `setUpdatedContainerLocation`, `sortDatanodes`, and `slimLocationVersion`.

## Control flow
Most read operations normalize through bucket layout. `lookupKey` reads `OmKeyInfo` under bucket read lock via `readKeyInfo`, then, unless the request is a head operation, adds READ block tokens, refreshes pipeline data from SCM, and optionally sorts datanodes by client distance. `getKeyInfo` follows the same shape but uses SCM container-location cache and supports forced cache refresh. `readKeyInfo` normalizes key paths, chooses FSO or non-FSO lookup, marks legacy/OBS keys as files, slims old location versions when requested, and can restrict a multipart key response to one part number.

Filesystem status has separate paths. Non-FSO `getOzoneFileStatus` checks root bucket, direct key, trailing-slash directory key, then synthesizes a fake directory if a descendant key proves the path is a prefix. FSO `getOzoneFileStatusFSO` delegates to `OMFileRequest.getOMKeyInfoIfExists` and only refreshes/sorts block locations for file entries. `lookupFile` wraps file status, rejects directories with `NOT_A_FILE`, and adds READ block tokens for non-head calls.

`listStatus` for FSO buckets delegates to `OzoneListStatusHelper` and post-processes block locations. Non-FSO listing first probes table cache into a sorted map, then seeks the RocksDB iterator, merging cache and DB results, synthesizing immediate-child fake directories for flat key names, filtering deleted cache entries, slimming location versions, refreshing cached container locations, and sorting datanodes if requested.

Deletion discovery walks metadata tables with bucket-prefix iterators. `getPendingDeletionKeys` converts reclaimable `RepeatedOmKeyInfo` versions into `DeletedBlock` and `BlockGroup` payloads while retaining non-reclaimable versions in `keysToModify`. FSO subdirectory and subfile deletion use `gatherSubPathsWithIterator` from an object-id path prefix and transform child records into full-path `OmKeyInfo`.

Multipart listing is bucket-locked. `listMultipartUploads` asks metadata manager for one extra result when paginating and sets next markers from the last returned entry. `listParts` loads `OmMultipartKeyInfo`, filters by part marker, computes part names, extracts eTags, derives replication config from a part or falls back to the open key, and returns truncation state.

ACL checks resolve bucket links before reading key metadata. `checkAccess` treats missing READ keys as allowed for OzoneFS compatibility, recursively checks child ACLs only for recursive DELETE, and otherwise checks key ACLs via `OzoneAclUtil`.

## State and persistence behavior
Persistent state is in OM metadata tables accessed through `OMMetadataManager`: key, file, directory, deleted, deleted directory, multipart, snapshot renamed, open key, bucket, and snapshot-adjacent tables. This class mostly reads or selects pending entries; writes are performed by OM request handlers and background services. Transient state includes service instances, the DNS mapper, and updated in-memory `OmKeyInfo` pipeline/token/location data returned to clients. Generated block tokens and encryption info are not persisted here. Fake directory `OmKeyInfo` objects are synthesized for responses and are not inserted into the DB.

## Dependencies and integration points
The implementation integrates with SCM for block deletion, container pipelines, and container-location cache; with KMS for encrypted data encryption keys; with OM locking for bucket-scoped metadata consistency; with OM background services for deletion, open key cleanup, MPU cleanup, snapshots, and compaction; with Ratis-visible metadata through OM managers; with topology mapping for datanode ordering; and with protocol helper classes such as `OmKeyArgs`, `OmKeyInfo`, `OzoneFileStatus`, `OmMultipartUploadList`, and `PendingKeysDeletion`.

## Risks and edge cases
The code mutates returned `OmKeyInfo` objects by slimming location versions, setting file flags, updating pipelines, setting block tokens, and filtering multipart part locations. Callers must not assume immutable metadata snapshots. Non-FSO fake directory discovery has race-handling code for cache deletes and DB flushes, but still depends on lexicographic path boundaries. `getNextGreaterString` increments the last byte of a key prefix and assumes non-empty valid persisted UTF-8-style key data. `listParts` can throw `IllegalStateException` if the MPU open key is missing. `sortDatanodes` depends on DNS/rack resolution and returns null client nodes when resolution fails, leaving sorting to cluster map behavior. Several service start paths catch and log snapshot service IOExceptions rather than failing OM startup.

Potential test-sensitive defects include `decNumS3Buckets` in `OMMetrics`, not here, but this class consumes those metrics elsewhere; `getBucketInfo` can return null and some callers validate while others use layout after a null check. Snapshot service mutual exclusion between defrag and SST filtering is configuration-dependent and should be tested when both intervals are positive.

## Test signals
Useful tests should cover legacy, OBS, and FSO bucket lookups; head versus non-head requests; block token enablement; latest-version location slimming; multipart part-number filtering; cache and DB merge behavior in non-FSO `listStatus`; fake directory synthesis; recursive ACL deletion checks; deletion queue filtering and `keysToModify`; SCM pipeline refresh failures mapped to `SCM_GET_PIPELINE_EXCEPTION`; FSO subpath deletion transforms; and lifecycle start/stop idempotency for all background services.
