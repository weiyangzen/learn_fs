## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneMultipartUploadPartListParts.java

### Purpose
`OzoneMultipartUploadPartListParts` represents the response for listing parts of a multipart upload, including replication config, pagination marker, truncation flag, and per-part metadata.

### Important APIs and Types
Constructors accept legacy type/factor or current `ReplicationConfig`. `addAllParts`, `addPart`, and getters manage `partInfoList`. Deprecated replication getters expose legacy compatibility. Nested immutable `PartInfo` stores part number, part name, modification time, size, and ETag.

### Control Flow
Parts are appended to an initially empty `ArrayList`. No sorting or duplicate checks are performed locally; ordering and validity are expected from the server response.

### State and Persistence Behavior
This is a mutable response DTO. It does not persist part state; multipart part lifecycle is controlled by OM through bucket APIs.

### Dependencies and Integration Points
It uses HDDS replication types and is returned by `OzoneBucket.listParts`.

### Risks and Edge Cases
The exposed part list is mutable. Deprecated replication factor conversion relies on `ReplicationConfig.getLegacyFactor`, which may be less meaningful for EC configs. No validation prevents duplicate part numbers.

### Test Signals
Tests should cover add/addAll behavior, truncation and marker fields, ETag preservation, legacy and current replication getters, and response ordering as produced by conversion code.
