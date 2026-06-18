# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/S3MultipartUploadCommitPartResponse.java

Purpose: `S3MultipartUploadCommitPartResponse` persists a committed MPU part and cleans obsolete part data.

Important APIs and types: It extends `OmKeyResponse`, stores multipart key, open part key, updated `OmMultipartKeyInfo`, optional `keyToDeleteMap`, optional open part key info to delete on abort race, bucket info, and bucket ID. It handles statuses `OK` and `NO_SUCH_MULTIPART_UPLOAD_ERROR`.

Control flow: `checkAndUpdateDB` has a special abort-race path: if the MPU no longer exists, it moves the open part to deleted table. On OK, `addToDBBatch` writes obsolete parts to deleted table, updates multipart info table, deletes the open part key, and updates bucket used bytes.

State and persistence behavior: It mutates multipart info, open-key/open-file, deleted, and bucket tables. It can write deleted-table state even for a non-OK abort-race status.

Dependencies and integration points: It integrates S3 commit-part request logic, overwrite handling, abort races, bucket layout routing, and key deletion service.

Risks and test signals: Tests should cover normal commit, overwrite part cleanup, no-such-upload abort race cleanup, bucket update, open-key deletion, and null optional maps.
