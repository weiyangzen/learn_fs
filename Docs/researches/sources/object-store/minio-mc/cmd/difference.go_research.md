# sources/object-store/minio-mc/cmd/difference.go

Purpose: Core differ engine for comparing sorted source and target object/bucket streams.

Important APIs/types/functions: `differType`, `getSourceModTimeKey`, `activeActiveModTimeUpdated`, `metadataEqual`, `bucketObjectDifference`, `objectDifference`, `bucketDifference`, `differenceInternal`, and `difference`.

Control flow: `differenceInternal` merges two sorted channels, emits only-in-first/second messages, normalizes UTF-8/NFC path suffixes, compares object type, size, active-active source modtime metadata, and optionally metadata maps. It stops early for source-listing-only mode and propagates stream errors.

State and persistence: Stateless stream processing. Uses buffered output channel.

Dependencies/integration: Consumes `ClientContent` listings from `Client` implementations and `mirrorOptions`. Handles MinIO and filesystem error classes.

Risks: Requires both streams to be sorted consistently by normalized suffix. In the type-diff branch, the loop continues without advancing channels, which is a potential infinite loop if reached. Metadata comparison uses `&&` between user metadata and system metadata inequality, so a difference in only one map may be missed.

Test signals: No direct tests for `differenceInternal`; this is a high-risk area for focused regression tests.
