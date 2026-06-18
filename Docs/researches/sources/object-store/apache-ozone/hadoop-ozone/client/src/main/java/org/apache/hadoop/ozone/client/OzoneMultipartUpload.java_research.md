## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneMultipartUpload.java

### Purpose
`OzoneMultipartUpload` represents one in-flight multipart upload, including its volume, bucket, key, upload ID, creation time, and replication configuration.

### Important APIs and Types
It has a deprecated constructor for legacy replication type/factor and a current constructor taking `ReplicationConfig`. Getters expose identifiers, creation time, and replication config. Deprecated getters adapt replication config back to legacy type/factor.

### Control Flow
Construction stores values directly or converts legacy type/factor with `ReplicationConfig.fromTypeAndFactor`. `setCreationTime` allows updating creation time after construction.

### State and Persistence Behavior
This is a mutable local DTO because `creationTime` can be set. Upload state itself persists in OM and is manipulated through `OzoneBucket` multipart APIs.

### Dependencies and Integration Points
It integrates with HDDS replication types and is held by `OzoneMultipartUploadList`, returned by `listMultipartUploads`.

### Risks and Edge Cases
Legacy replication getters assume non-null replication config. Mutable creation time can desynchronize from server state if changed by callers.

### Test Signals
Tests should verify legacy conversion, current replication config preservation, and list-response serialization/compatibility.
