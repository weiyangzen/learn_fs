# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/common/BekInfoUtils.java

## Purpose

`BekInfoUtils` provides common bucket encryption key validation and metadata enrichment for OM bucket encryption flows.

## Important APIs and Types

- `getBekInfo(KeyProviderCryptoExtension kmsProvider, BucketEncryptionInfoProto bek)` validates a KMS provider and requested key, fetches KMS metadata, warms encrypted key pools, and returns a populated `BucketEncryptionInfoProto`.

## Control Flow

The method rejects a null KMS provider with `INVALID_KMS_PROVIDER`, rejects a missing key name with `BUCKET_ENCRYPTION_KEY_NOT_FOUND`, fetches key metadata by key name, rejects missing KMS metadata with the same not-found result, warms encrypted keys for the key name, builds a new bucket encryption info proto with the key name, `ENCRYPTION_ZONES` crypto protocol version, and cipher suite converted from KMS metadata, then returns it.

## State and Persistence

The utility is stateless. It may cause KMS-side or provider-side encrypted data encryption key pools to warm, but it does not persist OM metadata itself. The returned proto is later persisted by bucket creation/update flows.

## Dependencies and Integration Points

It depends on Hadoop KMS `KeyProviderCryptoExtension`, `KeyProvider.Metadata`, Hadoop `CipherSuite`, OM `OMException`, `BucketEncryptionInfoProto`, and `OMPBHelper` conversion helpers.

## Risks and Edge Cases

`bek.getKeyName() == null` is used for validation; depending on protobuf defaults, empty strings may pass and fail only at KMS lookup. KMS latency/errors propagate as `IOException`. Warm-up failures will fail the operation. Cipher conversion depends on provider metadata containing a supported cipher name.

## Test Signals

Tests should cover null provider, missing key name, nonexistent KMS key, valid metadata conversion, KMS IOException propagation, and warm-up invocation.
