## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeyCreateRequestWithFSO.java

**Purpose:** Adapts the base key-create suite to FSO layout and adds coverage for `.snapshot` appearing as a normal path segment when it is not the reserved root snapshot namespace.

**Important APIs/types/functions:** Overrides `addToKeyTable`, `checkCreatedPaths`, `checkIntermediatePaths`, `getOpenKey`, `getOzoneKey`, `getOMKeyCreateRequest`, and `getBucketLayout`. Uses `OMKeyCreateRequestWithFSO`, `OmDirectoryInfo`, `OmBucketInfo`, `OmVolumeArgs`, `OzoneFSUtils`, `OMRequestTestUtils.addFileToKeyTable`, and FSO open-file key helpers.

**Control flow:** Valid snapshot-word tests create keys such as `.snapshota/key` and `a/.snapshot/b/c/key`, pre-execute them, validate/update cache, and assert success plus returned key name. Inherited create tests call overridden helpers that normalize FSO paths, assert intermediate directory rows exist, derive parent IDs, and locate open files by volume ID, bucket ID, parent ID, leaf name, and client ID.

**State and persistence behavior:** Successful FSO creates populate directory rows for parents and open-key rows keyed by `getOpenFileName`. Existing committed files are inserted with leaf file names and parent object IDs. The root-parent case uses the bucket object ID.

**Dependencies and integration points:** Integrates create logic with FSO metadata tables, bucket/volume object IDs, filesystem path normalization, and inherited tests for generation, ETag, quota, metadata, ACL, and SCM behavior. It depends on `BucketLayout.FILE_SYSTEM_OPTIMIZED` dispatch to instantiate the FSO request class.

**Risks:** Risks are missing intermediate directory creation, using unnormalized or full-path names in FSO DB keys, mishandling `.snapshot` as reserved outside the root namespace, and test fallback sentinel IDs masking missing bucket setup.

**Test signals:** Non-null directory/open-key rows, correct parent ID traversal, success for valid `.snapshot` segments, and inherited create-suite assertions under FSO layout provide the main confidence signals.
