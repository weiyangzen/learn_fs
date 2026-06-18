## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneBucket.java

### Purpose
`OzoneBucket` is the client-side representation and operation facade for a bucket inside a volume. It exposes bucket metadata, ACLs, quota and replication configuration, key CRUD, stream-key creation, multipart upload, file-system style APIs, object tagging, owner updates, and key listing for both object-store and file-system-optimized bucket layouts.

### Important APIs and Types
- Core state: `volumeName`, `name`, `defaultReplication`, `storageType`, `versioning`, usage/quota counters, timestamps, encryption key name, link source fields, `BucketLayout`, owner, pending-delete counters, and an `OzoneObj` for ACL operations.
- Mutating bucket APIs: `setStorageType`, `setVersioning`, `clearSpaceQuota`, `clearNamespaceQuota`, `setQuota`, `setReplicationConfig`, `setEncryptionKey`, `setOwner`.
- Key write APIs: `createKey`, deprecated type/factor overloads, conditional `rewriteKey`, `createKeyIfNotExists`, `rewriteKeyIfMatch`, stream variants, and multipart-part stream creation.
- Key read/list/delete APIs: `readKey`, `getKey`, `headObject`, `listKeys`, `deleteKey`, `deleteDirectory`, `deleteKeys`, `renameKey`, deprecated `renameKeys`.
- File-system APIs: `getFileStatus`, `createDirectory`, `readFile`, `createFile`, `createStreamFile`, `listStatus`, and `listStatusLight`.
- Multipart APIs: initiate, create part, complete with optional conditional generation/ETag, abort, list parts, and list uploads.
- Nested types: `Builder`, `KeyIterator`, `KeyIteratorWithFSO`, and `KeyIteratorFactory`.

### Control Flow
Most public operations directly delegate to `ClientProtocol`, then update local cached fields only after successful mutations. Quota clear methods first fetch fresh bucket details to preserve the quota dimension that is not being cleared. Key creation defaults to bucket replication unless explicit replication is provided; stream creation normalizes null replication back to the bucket default.

`listKeys` chooses a normal `KeyIterator` or FSO-aware `KeyIteratorWithFSO` based on `bucketLayout.isFileSystemOptimized()`. The normal iterator pages through `proxy.listKeys`, and its shallow mode uses `listStatusLight` to avoid recursively listing all descendants. It calculates a delimiter prefix, fetches a first key by `listKeys` when needed, includes the prefix object for delimiter semantics, and converts `OzoneFileStatusLight` to `OzoneKey`.

`KeyIteratorWithFSO` implements depth-first traversal over file-system-optimized directory metadata. It builds a stack of `(prefix,startKey)` pairs from the requested prefix and previous key, calls `listStatusLight` for immediate children, pushes sibling and child paths back onto the stack, and removes internal placeholder start keys so list-key semantics match object-store expectations. Its shallow mode additionally adjusts the start key to an immediate child and checks whether a prefix exists when no first start key is found.

### State and Persistence Behavior
`OzoneBucket` caches bucket metadata at construction and updates a subset of fields after successful proxy mutations. Actual bucket, key, multipart, ACL, tag, and file-system state persists in OM and DataNodes. Iterator state is local: current page iterator, last current value, delimiter prefix flags, DFS stack, and internal `removeStartKey`. Link buckets track `sourceVolume`, `sourceBucket`, and `sourcePathExist`; utility code may set `sourcePathExist` to false for orphan links.

### Dependencies and Integration Points
The class depends heavily on `ClientProtocol`, OM helper types (`OmKeyInfo`, `OmMultipartInfo`, `OzoneFileStatus`, `OzoneFileStatusLight`, `ErrorInfo`), HDDS replication/storage types, `OzoneDataStreamOutput`, `OzoneInputStream`, `OzoneOutputStream`, `OzoneObjInfo`, and `OzoneFSUtils`. It is a central integration point for object-store users, S3 gateway semantics, Ozone FS APIs, and multipart upload flows.

### Risks and Edge Cases
The FSO and shallow list algorithms are complex and rely on lexicographic path comparisons, normalized keys, trailing slash handling, and `listStatusLight` including or excluding start keys in specific ways. Regressions can cause duplicates, skipped prefixes, infinite pagination, or incorrect directory marker behavior. Local cached fields may become stale if other clients mutate bucket settings. `setOwner` updates local owner regardless of the boolean result from the proxy. The public constructors/builders do little validation beyond requiring a non-null proxy in `newBuilder`.

### Test Signals
High-value tests include normal and FSO `listKeys` pagination, shallow delimiter listing with prefixes ending with and without `/`, previous-key continuation inside nested directories, prefix-as-directory inclusion, file-vs-directory conversion to `OzoneKey`, quota clear preserving the other quota dimension, conditional write delegation, multipart completion with conditions, object tagging round trips, and stale-cache expectations after external mutation.
