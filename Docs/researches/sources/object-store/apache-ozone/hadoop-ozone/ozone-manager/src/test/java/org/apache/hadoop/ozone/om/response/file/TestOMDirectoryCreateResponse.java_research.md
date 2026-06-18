# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/file/TestOMDirectoryCreateResponse.java

Purpose: Tests `OMDirectoryCreateResponse` for the default bucket layout, ensuring directory creation writes the key table and updates bucket namespace accounting.

Important APIs/types/functions: Uses `OMDirectoryCreateResponse`, `OMDirectoryCreateRequest.Result.SUCCESS`, `BucketLayout.DEFAULT`, `OmKeyInfo`, `OmBucketInfo`, `OzoneFSUtils.addTrailingSlashIfNeeded`, `OMRequestTestUtils.createOmKeyInfo`, and `getOzoneDirKey`.

Control flow: The test builds a directory-style `OmKeyInfo`, creates a bucket info with random `usedNamespace`, constructs a successful `CreateDirectory` OM response, calls `addToDBBatch`, commits, then asserts the directory key exists in the default key table and the bucket row records the same namespace count.

State/persistence: Adds one directory marker to `keyTable(DEFAULT)` and one bucket row to `bucketTable`.

Dependencies/integration: Exercises legacy directory create response behavior through the real OM metadata manager and batch operation.

Risks/test signals: Parent list is empty, so it does not cover recursive parent creation. The signal is table placement under `getOzoneDirKey` plus bucket namespace persistence.
