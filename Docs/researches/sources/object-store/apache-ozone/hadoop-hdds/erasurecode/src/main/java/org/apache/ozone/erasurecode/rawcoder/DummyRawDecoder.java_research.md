<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/DummyRawDecoder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/DummyRawDecoder.java

## Purpose
`DummyRawDecoder` is a no-op decoder used for plumbing and negative/placeholder tests.

## Important APIs, Types, and Functions
It extends `RawErasureDecoder`, exposes only a constructor, and overrides both `doDecode` overloads with empty bodies.

## Control Flow
All normal validation and input position advancement happen in `RawErasureDecoder`; the concrete decode operation intentionally writes nothing.

## State and Persistence Behavior
It has no mutable state beyond inherited replication config.

## Dependencies and Integration Points
It is created by `DummyRawErasureCoderFactory` and used by `TestDummyRawCoder` to verify framework behavior around no-op coders.

## Risks and Test Signals
Risk is accidental production selection if registry/provider configuration treats `dummy` as a usable codec. Test signals ensure dummy outputs remain empty/zero and that dummy factory names do not collide with real coders.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/DummyRawDecoder.java -->
