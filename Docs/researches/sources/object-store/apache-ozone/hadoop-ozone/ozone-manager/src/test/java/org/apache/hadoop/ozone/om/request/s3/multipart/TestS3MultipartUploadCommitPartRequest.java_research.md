# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/multipart/TestS3MultipartUploadCommitPartRequest.java

Purpose: tests default-layout `S3MultipartUploadCommitPartRequest`, including successful part commit, missing MPU/key/bucket errors, overwrites, uncommitted block deletion, and empty-part handling.

Important APIs and types: `S3MultipartUploadCommitPartRequest`, `S3MultipartUploadCommitPartResponse`, `S3InitiateMultipartUploadRequest`, `OmMultipartKeyInfo`, `PartKeyInfo`, `OmKeyInfo`, `RepeatedOmKeyInfo`, `OmKeyLocationInfo`, protobuf `KeyLocation`, `RatisReplicationConfig`, and `Time`.

Control flow: success creates volume/bucket, initiates MPU, creates a part open key, pre-executes commit with part number 1, validates, then checks multipart info and open-key tables. Negative tests skip creating MPU or open part key or bucket and verify the expected error. Overwrite tests first commit a part, then commit the same part number again with different client ID and block locations. Uncommitted-block tests create an open part key with more allocated locations than committed locations.

State and persistence behavior: commit adds/updates a `PartKeyInfo` in `multipartInfoTable`, keeps the MPU open key marked multipart, and removes the individual part open key. When overwriting a part, the response carries old part key data in `getKeyToDelete`. When allocated blocks exceed committed blocks, the response carries only uncommitted locations for deletion. Combining overwrite with uncommitted blocks returns two deletion entries. Empty part commits intentionally do not return a delete map for uncommitted blocks.

Dependencies and integration points: uses base initiate/commit preExecute helpers and `OMRequestTestUtils.addKeyToTable` to simulate data upload through key-create before commit. `getKeyLocation` creates deterministic block IDs for assertions.

Risks covered: block leak on overwrite or partial commit, accidental deletion for empty parts, wrong status when parent/key state is absent, and failure to remove part open keys. FSO subclass reuses these tests with different key naming.

Test signals: statuses `OK`, `NO_SUCH_MULTIPART_UPLOAD_ERROR`, `KEY_NOT_FOUND` or `DIRECTORY_NOT_FOUND` for FSO, and `BUCKET_NOT_FOUND`; table sizes and null/present rows; equality of committed block lists; deletion-map size and location counts.
