## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/multipart/S3MultipartUploadCommitPartRequest.java

Purpose: `S3MultipartUploadCommitPartRequest` commits one uploaded part into an in-progress multipart upload. It removes the temporary open part key, records part metadata in the multipart-info table, accounts for quota, and schedules old overwritten part/uncommitted block cleanup.

Important APIs/types/functions: `preExecute` normalizes the key and checks open-key WRITE ACL using the client ID. `validateAndUpdateCache` uses `getOpenKey`, `getOmKeyInfo`, `getPartName`, `OmMultipartKeyInfo.addPartKeyInfo`, `getOldVersionsToCleanUp`, `getOzoneDeletePathKey`, `wrapUncommittedBlocksAsPseudoKey`, `addKeyInfoToDeleteMap`, and `S3MultipartUploadCommitPartResponse`. Validators cover EC finalization and old-client layout compatibility.

Control flow: Under bucket lock, it validates volume/bucket, computes the multipart-info key, loads multipart info, computes the temporary open key from client ID, loads the uploaded part `OmKeyInfo`, merges user metadata, updates location info and data size from `KeyArgs`, computes the part name from ozone key/upload ID/part number, verifies multipart info exists, remembers any overwritten part, adds the new `PartKeyInfo`, updates the multipart-info row, tombstones the open part key, adjusts bucket used bytes by the new part minus overwritten part, and adds overwritten/uncommitted block pseudo keys to the delete map for response cleanup.

State and persistence behavior: The multipart-info table is updated with the part map and update ID. The temporary open-key row is tombstoned. Bucket used bytes increase by the replicated size of the new committed part minus overwritten part size. Old overwritten parts and uncommitted blocks are not directly written here; they are carried in the response's delete map.

Dependencies and integration points: This request integrates MPU upload-part completion with open-key commit semantics, quota enforcement, delete-table cleanup, audit of upload ID/part number/part name, metrics, and layout-feature validators.

Risks and edge cases: If multipart info disappeared between upload and commit, the uploaded part must still be cleaned by response/error handling; the code throws no-such-upload after loading the open key. Overwriting a part must avoid double-counting quota and must delete the old part. Part names and ETags must remain compatible with complete-MPU validation.

Test signals: Cover first part commit, part overwrite, missing open part, missing multipart info, quota exceeded, uncommitted block cleanup, ETag in response, metrics/audit, EC gating, and old-client layout rejection.
