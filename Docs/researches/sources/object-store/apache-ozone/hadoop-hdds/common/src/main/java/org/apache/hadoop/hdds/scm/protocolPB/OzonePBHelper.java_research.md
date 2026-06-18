# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/protocolPB/OzonePBHelper.java

## Purpose
Small protobuf conversion helper for token-related messages and low-allocation `ByteString` creation.

## Important APIs and types
`getFixedByteString(Text)` caches `Text` to UTF-8 `ByteString` for fixed, small string domains such as token kind. `getByteString(byte[])` returns `ByteString.EMPTY` for empty arrays. `tokenFromProto` and `protoFromToken` convert between Hadoop `Token<T>` and `HddsProtos.TokenProto`.

## Control flow and state
The only state is a static `ConcurrentHashMap` cache without eviction. Token conversion copies identifier/password bytes and preserves kind/service values.

## Dependencies and integration points
Used by protobuf-facing container token code. It depends on Hadoop `Token`, `TokenIdentifier`, `Text`, and unshaded protobuf `ByteString` to avoid Hadoop protobuf shading issues.

## Risks and test signals
Because the fixed-string cache is unbounded, callers should use it only for small finite domains. Tests should verify token round trips, empty byte handling, and service/kind byte encoding compatibility.
