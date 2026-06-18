# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/util/TestS3Utils.java

## Purpose
JUnit 5 coverage for `S3Utils`, especially S3 storage-class-to-Ozone replication resolution, canonical user id generation, and Content-MD5 validation. It guards the S3 gateway contract that AWS-facing headers map to the correct Ozone replication settings and S3 error codes.

## Important APIs, types, and functions
The test drives `S3Utils.resolveS3ClientSideReplicationConfig`, `generateCanonicalUserId`, and `validateContentMD5`. It uses `S3StorageType`, `ECReplicationConfig`, `RatisReplicationConfig`, `ReplicationConfig`, `S3Owner`, `OS3Exception`, and `S3ErrorTable`. Parameter sources enumerate storage types, storage configs, client configs, and bucket configs.

## Control flow
Valid replication tests build the Cartesian product of allowed S3 storage type/config values and client/bucket defaults, call resolution, then independently compute expected precedence: S3 storage class overrides client and bucket config, client overrides bucket, and empty input returns null. Invalid tests expect `INVALID_STORAGE_CLASS`. MD5 tests compute valid and invalid client/server digests and assert either success or `INVALID_DIGEST`/`BAD_DIGEST`.

## State and persistence behavior
No persistent state is written. The only state is generated test data: replication config instances and digest encodings. Equality of replication objects is the key state signal.

## Dependencies and integration points
This file sits between S3 gateway request parsing and Ozone replication internals. It depends on HDDS replication config types, Apache Commons Hex/StringUtils, Java `MessageDigest`/Base64, and S3 error translation.

## Risks and edge cases
Coverage is intentionally combinatorial for valid replication inputs but only checks two invalid cases. Storage-class precedence or default EC policy changes will require expected-value updates. MD5 checks cover malformed Base64, wrong length, missing value, and mismatched digest.

## Test signals
Signals are exact replication object equality/nullness, canonical owner id equality, and precise S3 error code assertions for digest and storage-class failures.
