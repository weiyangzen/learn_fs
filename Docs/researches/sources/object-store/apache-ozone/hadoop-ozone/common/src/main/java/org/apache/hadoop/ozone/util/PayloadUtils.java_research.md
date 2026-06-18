# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/util/PayloadUtils.java

Purpose: Utility for generating deterministic-sized payload buffers for RPC/testing/benchmark requests.

Important APIs and types: Static `MAX_SIZE`, random 1024-byte `SEED`, `generatePayload`, `generatePayloadProto2`, and `generatePayloadProto3`.

Control flow: `generatePayload` allocates a byte array capped at `MAX_SIZE`, repeatedly copies the seed into it, asserts the final index, and returns the array. Proto helpers unsafe-wrap the generated array into either protobuf v2 or Ratis-shaded protobuf ByteString.

State and persistence behavior: Static seed is generated once per JVM. No persistence. Returned unsafe-wrapped ByteStrings share the generated array contents.

Dependencies and integration points: Used by echo/RPC payload tools or tests that need bounded payload generation across protobuf variants.

Risks: Negative payload sizes cause `NegativeArraySizeException` because there is no explicit validation. Large sizes allocate up to roughly 2 GiB, which can pressure memory. Unsafe wrapping assumes callers do not mutate arrays after wrapping; here arrays are not exposed except through the wrapper path.

Test signals: Verify exact size for small/zero/max-overflow requests, repeated seed-copy pattern, proto2/proto3 empty behavior, and negative-size failure.
