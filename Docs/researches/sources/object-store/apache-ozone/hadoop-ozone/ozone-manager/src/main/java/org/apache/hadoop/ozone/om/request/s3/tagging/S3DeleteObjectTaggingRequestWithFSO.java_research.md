## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tagging/S3DeleteObjectTaggingRequestWithFSO.java

Purpose: `S3DeleteObjectTaggingRequestWithFSO` removes all tags from an FSO file key. It rejects directory targets because object tagging applies to objects/files, not directories.

Important APIs/types/functions: The overridden `validateAndUpdateCache` uses `OMFileRequest.getOMKeyInfoIfExists`, `OzoneFileStatus`, `OzoneFSUtils.getFileName`, `getOzonePathKey(volumeId,bucketId,parentId,fileName)`, and `S3DeleteObjectTaggingResponseWithFSO`. It inherits preExecute from the base tagging request.

Control flow: Under bucket lock, it validates volume/bucket, resolves the FSO path to an `OzoneFileStatus`, fails with `KEY_NOT_FOUND` when absent, rejects directories with `NOT_SUPPORTED_OPERATION`, resets key name to the leaf file name, computes the FSO file-table DB key from object IDs, clears tags, sets update ID, writes the layout key table cache entry, returns an FSO response, and logs metrics.

State and persistence behavior: Only the FSO file table row for the target file is updated; directory rows are never modified because directory tagging is unsupported. Modification time remains unchanged, matching S3 semantics. The response includes volume ID and bucket ID for replay.

Dependencies and integration points: It integrates S3 object tagging with FSO path lookup, file-table persistence, bucket locks, metrics, and FSO-specific response replay. Unlike the base class, this override does not call `markForAudit`, which is a notable behavioral difference.

Risks and edge cases: Directory rejection is explicit and must remain stable for clients. Leaf-name resetting and path-ID key computation are required to avoid corrupting FSO rows. The missing audit call may be intentional or a gap compared with the non-FSO implementation.

Test signals: Cover FSO file tag deletion, FSO directory rejection, missing path, nested paths, unchanged modification time, response replay with IDs, metric increments, and audit parity with the non-FSO path.
