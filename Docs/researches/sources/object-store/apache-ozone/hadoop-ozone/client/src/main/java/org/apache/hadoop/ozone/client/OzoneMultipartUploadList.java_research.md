## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneMultipartUploadList.java

### Purpose
`OzoneMultipartUploadList` is the client-visible response wrapper for listing in-flight multipart uploads.

### Important APIs and Types
The constructor requires a non-null upload list and stores `nextKeyMarker`, `nextUploadIdMarker`, and `isTruncated`. Getters expose all fields, and `setUploads` can replace the list.

### Control Flow
The only validation is `Objects.requireNonNull(uploads)`. Pagination markers are passive values supplied by the server-side conversion path.

### State and Persistence Behavior
This is a mutable local DTO. Replacing uploads does not affect OM multipart state.

### Dependencies and Integration Points
It contains `OzoneMultipartUpload` objects and is returned from `OzoneBucket.listMultipartUploads` as S3-style pagination state.

### Risks and Edge Cases
`setUploads` does not enforce non-null after construction. The upload list is exposed directly, so callers can mutate it.

### Test Signals
Tests should verify null-constructor rejection, marker propagation, truncation flag propagation, and mutability expectations.
