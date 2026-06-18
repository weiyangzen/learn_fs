<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/TestCodecRegistry.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/TestCodecRegistry.java

## Purpose
`TestCodecRegistry` verifies raw coder registration, lookup, ordering, conflict handling, and codec name coverage.

## Important APIs, Types, and Functions
Tests include `testGetCodecs`, `testGetCoders`, wrong lookup cases, `testUpdateCoders`, `testGetCoderNames`, and `testGetCoderByName`. It defines an inner incorrect RS factory to test duplicate coder-name rejection.

## Control Flow
Tests query the singleton registry, assert `rs` and `xor` codecs, verify native factories are ordered before Java factories, update the registry with a conflicting factory, and assert coder arrays remain unchanged.

## State and Persistence Behavior
The test mutates singleton registry state via `updateCoders`, so ordering and isolation matter across tests.

## Dependencies and Integration Points
It depends on AssertJ/JUnit, `CodecRegistry`, `ECReplicationConfig`, and factory classes.

## Risks and Test Signals
Risks include singleton state leakage and assumptions about service-loader ordering. Passing tests signal correct native-first ordering, duplicate rejection, and lookup by coder name.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/TestCodecRegistry.java -->
