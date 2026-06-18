
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/client/OzoneBucketStub.java

Purpose: in-memory `OzoneBucket` for endpoint tests, modeling keys, key bytes, multipart uploads, ACLs, replication config, directories, and object tags.

Important APIs and control flow: key creation returns output streams whose `close` commits bytes and `OzoneKeyDetails` into maps. Conditional create/rewrite methods throw OM exceptions for existing/missing/ETag mismatch. Stream key creation writes through a byte buffer. Reads/list/head use sorted key maps and support shallow listing by delimiter-like path truncation. Multipart initiation stores upload metadata; part upload records numbered parts and ETags; completion checks part order and ETags, concatenates bytes, writes final key details, and returns completion info. Abort removes upload state. Tagging methods mutate tags stored on key details. Directory creation inserts non-file zero-length key details.

State, dependencies, integration: in-memory maps hold `keyDetails`, `keyContents`, `keyToMultipartUpload`, and `partList`; ACLs are an array list; replication config is mutable. Integrated by `OzoneVolumeStub`, `ClientProtocolStub`, and endpoint tests for object/bucket listing, ACL, multipart, and tagging scenarios.

Risks and test signals: no synchronization and many production features are simplified. `deleteKey` removes metadata but leaves `keyContents`, so stale bytes may remain if read by direct map path. Shallow listing uses simple string splitting and may diverge from OM listing edge cases. Multipart completion does not clear upload/part state after success. Endpoint tests in this subset validate listing, owners, multipart abort, ACL handling, and bucket-not-empty behavior through this stub.
