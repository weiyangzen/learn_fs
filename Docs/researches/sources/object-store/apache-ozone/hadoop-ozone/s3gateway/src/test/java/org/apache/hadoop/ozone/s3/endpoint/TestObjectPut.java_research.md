<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectPut.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectPut.java

## Purpose
Large unit suite for S3 `PUT Object` and `CopyObject` behavior across metadata, tags, conditionals, checksums, signed chunks, replication, and FSO directory creation.

## Important APIs, types, and functions
Uses `ObjectEndpoint.put`, `EndpointTestUtils.put/putDir`, `OzoneClientStub`, `OzoneBucket`, `OzoneKeyDetails`, `S3Consts` headers for tags/copy/storage/signed payload, `S3Utils.parseETag/urlEncode`, `S3ErrorTable`, `EndpointBase.getMD5DigestInstance`, and `S3ConditionalRequest`-driven headers.

## Control flow
Setup creates source, destination, and FSO buckets. Parameterized PUT verifies RATIS and EC replication with zero/nonzero content. Tag tests cover valid tags, key-only tags, duplicates, length limits, and tag count limits. Signed-chunk PUT decodes chunk framing. CopyObject tests cover metadata COPY/REPLACE, tag COPY/REPLACE, source/destination errors, invalid directives, source and destination ETag preconditions, and destination `If-Match`/`If-None-Match`. Additional tests cover invalid storage class, empty object, incomplete body rejection, content MD5 success/failure, digest reset on exceptions, FSO directory creation/no-overwrite, and ETag parsing.

## State and persistence behavior
The stub bucket persists object bytes, size, replication config, ETag metadata, custom metadata, and tags. Failure paths must avoid committing partial destination keys and must reset thread-local digest instances for reuse.

## Dependencies and integration points
This is central coverage for S3 object write semantics, Ozone key creation/copy, checksum validation, AWS signed payload decoding, tag parsing, storage-class mapping, FSO directory APIs, and conditional write enforcement.

## Risks and edge cases
The suite is broad but stub-based; real stream failure timing, large object copies, encryption, and concurrent conditional writes are not covered. Some mock header state is reused within tests, so ordering changes can affect expectations.

## Test signals
Signals include persisted content/metadata/tags/replication, S3 error codes/messages, ETag equality, absence of partial keys after failures, digest `reset()` verification, and HTTP success response checks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectPut.java -->
