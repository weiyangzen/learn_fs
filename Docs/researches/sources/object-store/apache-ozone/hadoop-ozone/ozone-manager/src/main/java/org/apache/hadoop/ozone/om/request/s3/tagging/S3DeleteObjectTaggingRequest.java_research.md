## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tagging/S3DeleteObjectTaggingRequest.java

Purpose: `S3DeleteObjectTaggingRequest` removes all object tags from a key in non-FSO layouts while preserving the object's content modification time. It implements the S3 delete-object-tagging operation.

Important APIs/types/functions: `preExecute` normalizes the key and checks WRITE ACL through `resolveBucketAndCheckKeyAcls`. `validateAndUpdateCache` uses bucket locks, `validateBucketAndVolume`, flat `getOzoneKey`, key table lookup, `OmKeyInfo.toBuilder().setTags(Collections.emptyMap()).setUpdateID(...)`, and `S3DeleteObjectTaggingResponse`.

Control flow: Under bucket lock, the request validates volume/bucket, loads the key table row, fails with `KEY_NOT_FOUND` if absent, clears tags to an empty map, sets update ID, writes the key table cache entry, constructs a delete-tagging response, releases the lock, audits, and updates success/failure metrics/logs.

State and persistence behavior: Only the key's tag map and update ID change. Modification time intentionally does not change because S3 last modified time should reflect object content changes, not tag changes. Persistence is staged through key-table cache.

Dependencies and integration points: It integrates S3 tagging APIs with OM key metadata, native ACL checks, bucket locks, audit under `OMAction.DELETE_OBJECT_TAGGING`, metrics, and `S3DeleteObjectTaggingResponse`.

Risks and edge cases: Missing keys are client failures. Clearing tags should not alter metadata, data size, block locations, or modification time. Failure logging is gated by `OMClientRequestUtils.shouldLogClientRequestFailure`, avoiding noisy logs for expected client errors.

Test signals: Cover deleting existing tags, deleting when tag map is already empty, missing key, unchanged modification time, cache update ID, audit, metrics, and authorization failure.
