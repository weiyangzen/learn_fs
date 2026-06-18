## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/multipart/S3InitiateMultipartUploadRequest.java

Purpose: `S3InitiateMultipartUploadRequest` starts an S3 multipart upload for non-FSO layouts. It generates an upload ID, normalizes and authorizes the key, creates an open-key row, creates a multipart-info row, and returns the upload ID to the client.

Important APIs/types/functions: `preExecute` normalizes key paths, sets `MultipartUploadID`, modification time, encryption info, user info, and resolves bucket links/checks CREATE ACL. `validateAndUpdateCache` creates `OmMultipartKeyInfo` and `OmKeyInfo`. Validators include `disallowInitiateMultiPartUploadWithECReplicationConfig` and `blockInitiateMPUWithBucketLayoutFromOldClient`. Dependencies include `OzoneConfigUtil.resolveReplicationConfigPreference`, `OMMultipartUploadUtils.getMultipartUploadId`, `OMFileRequest.verifyFilesInPath`, `getAclsForKey`, `KeyValueUtil`, and `S3InitiateMultipartUploadResponse`.

Control flow: Under the bucket lock, the request validates volume/bucket existence, computes the flat multipart DB key from volume/bucket/key/upload ID, optionally checks file-path conflicts when path normalization is active, resolves replication config, builds the empty open `OmKeyInfo` with ACLs, metadata, tags, owner, encryption info, object ID, and update ID, then writes open-key and multipart-info cache entries.

State and persistence behavior: The open-key table receives the future object state under a multipart key, and the multipart-info table receives upload metadata under the same multipart key. The key table is not updated until complete MPU. Multiple uploads for the same object are intentionally independent because upload ID is part of the DB key.

Dependencies and integration points: It integrates client S3 MPU initiation with OM key request ACL helpers, encryption metadata generation, default bucket replication config, prefix ACL inheritance, old-client layout validation, and OM layout-feature finalization for EC replication.

Risks and edge cases: Existing keys do not block initiation; conflict resolution happens on complete. EC requests are rejected until layout finalization. Path normalization and directory conflict checks only run when bucket layout/config require it. Missing bucket info can affect default replication fallback and ACL derivation.

Test signals: Cover upload ID creation, open-key and multipart-info cache entries, multiple initiations for same key, metadata/tag/encryption propagation, ACL inheritance, old-client rejection for non-legacy layouts, EC finalization gating, and path conflict handling.
