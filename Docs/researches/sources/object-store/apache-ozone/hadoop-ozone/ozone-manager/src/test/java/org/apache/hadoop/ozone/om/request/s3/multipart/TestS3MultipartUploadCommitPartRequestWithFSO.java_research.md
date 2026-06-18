# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/multipart/TestS3MultipartUploadCommitPartRequestWithFSO.java

Purpose: adapts commit-part coverage to FSO layout by overriding request factories, parent-path creation, and open-key derivation while inheriting the comprehensive commit-part tests from the default class.

Important APIs and types: `S3MultipartUploadCommitPartRequestWithFSO`, `S3InitiateMultipartUploadRequestWithFSO`, `BucketLayout.FILE_SYSTEM_OPTIMIZED`, `OmKeyInfo`, `OmKeyLocationInfoGroup`, `OzoneFSUtils`, `StringUtils`, `OMRequestTestUtils.addFileToKeyTable`, and metadata manager `getOpenFileName` and FSO multipart key helpers.

Control flow: inherited tests create keys under `a/b/c/<uuid>`. `createParentPath` creates parent directories and stores `parentID`. Overridden `addKeyToOpenKeyTable` builds an `OmKeyInfo` with parent/object IDs and optional location list, stores it in the FSO open-file table, and returns the FSO open-file key when needed. Request factory overrides instantiate FSO initiate and commit classes and set current-user UGI.

State and persistence behavior: part open keys and MPU open keys are addressed by numeric volume ID, bucket ID, parent ID, file name, and client ID or upload ID. The logical multipart-info row remains keyed by volume/bucket/full key/upload ID. The same inherited assertions validate deletion of part open keys, retained MPU open key, and multipart part map updates under FSO identity.

Dependencies and integration points: custom `doPreExecuteInitiateMPU` ensures FSO pre-execution assertions still hold. `OzoneFSUtils.getFileName` and `StringUtils.substringAfter` are path-splitting dependencies.

Risks covered: storing full paths as file names, wrong parent ID for committed parts, mismatched logical versus FSO keys, and broken inherited block deletion behavior under FSO. The class also exposes a risk if fixed `dirName` state and `parentID` are reused incorrectly across tests.

Test signals: inherited success/error/deletion-map assertions pass with FSO bucket layout and FSO key construction.
