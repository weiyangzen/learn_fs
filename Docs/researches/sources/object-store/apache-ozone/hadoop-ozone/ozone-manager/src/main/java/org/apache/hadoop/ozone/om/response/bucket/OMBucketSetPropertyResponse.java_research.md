# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/bucket/OMBucketSetPropertyResponse.java

Purpose: `OMBucketSetPropertyResponse` persists bucket property changes such as quotas, versioning, layout-related fields, or metadata updated by the request.

Important APIs and types: It stores one `OmBucketInfo`, annotates cleanup for `BUCKET_TABLE`, and writes through `putWithBatch`.

Control flow: Successful constructor captures the updated bucket info. `addToDBBatch` derives the bucket key from volume/bucket names and writes the table row.

State and persistence behavior: Only bucket-table state changes. Error responses enforce non-OK status and do not carry bucket info.

Dependencies and integration points: It is paired with bucket property request validation and replay.

Risks and test signals: Tests should assert updated fields are persisted, failed responses are no-op, and cleanup metadata includes the bucket table.
