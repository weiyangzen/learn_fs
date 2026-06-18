## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneVolume.java

### Purpose
`OzoneVolume` is the client-side representation and operation facade for an Ozone volume. It exposes volume metadata, ACL and quota mutations, owner changes, bucket create/get/list/delete operations, and ref-count information used by multi-tenancy or other locking features.

### Important APIs and Types
Core state includes `ClientProtocol`, name, admin, owner, quota bytes/namespace, used namespace, timestamps, ACL list, list cache size, `OzoneObj`, and `refCount`. Public methods expose getters, ACL mutation, owner/quota mutation, bucket operations, and `listBuckets`. The nested `Builder` constructs instances from OM data. `BucketIterator` pages through `proxy.listBuckets`.

### Control Flow
Mutating methods delegate to `ClientProtocol` and update local cached fields when successful. Quota clear methods fetch current volume details first so clearing one quota dimension preserves the other. `listBuckets` returns a `BucketIterator`, which fetches an initial page and then uses the last returned bucket name as the next `prevBucket` marker.

### State and Persistence Behavior
The object caches metadata locally but durable state is in OM. ACL changes update the local list only if the server reports success. `modificationTime` defaults to now when the builder supplies zero but is clamped not to precede creation time.

### Dependencies and Integration Points
It depends on `ClientProtocol`, `OzoneAcl`, `OzoneQuota`, `OzoneObjInfo`, `BucketArgs`, `OzoneBucket`, and `WithMetadata`. It is produced by `ObjectStore.getVolume` and used as the parent facade for bucket operations.

### Risks and Edge Cases
Cached state can become stale after external mutations. `setOwner` updates local owner regardless of the boolean result. `BucketIterator` wraps `IOException` in `RuntimeException`, so listing errors can surface outside checked-exception signatures. Builder fields such as ACL list should be populated by conversion paths; null ACLs would fail in constructor copy.

### Test Signals
Tests should cover ACL local cache updates, quota clear preserving the other quota, bucket listing across page boundaries, snapshot-filtered bucket listing, modification-time defaulting, ref-count getter, and owner update behavior when proxy returns false.
