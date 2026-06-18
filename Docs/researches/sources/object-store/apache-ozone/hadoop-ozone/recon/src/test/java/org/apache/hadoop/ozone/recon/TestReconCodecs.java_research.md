# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconCodecs.java

## Purpose
This JUnit test verifies binary persistence round trips for codecs used by Recon metadata tables.

## Important APIs and functions
`testContainerKeyPrefixCodec` creates a `ContainerKeyPrefix`, serializes it with singleton `ContainerKeyPrefixCodec.get()`, deserializes it, and asserts equality. `testIntegerCodec` performs the same persisted-format round trip for Hadoop `IntegerCodec`.

## Control flow, state, and persistence
The tests operate entirely in memory. They validate the byte-array persisted representation but do not write to RocksDB.

## Dependencies and integration points
The tested codec supports `ContainerKeyPrefix`, which is used by Recon container-to-key mapping. `IntegerCodec` is a generic DB codec used by table definitions.

## Risks and edge cases
The container prefix test uses `System.currentTimeMillis`, so equality depends on deterministic serialization of arbitrary long container IDs and key prefixes but does not check stable byte ordering. It only covers one key prefix and version value.

## Test signals
Strong signal for basic serialize/deserialize symmetry. It does not cover backward compatibility, malformed bytes, null handling, or lexicographic ordering expectations.
