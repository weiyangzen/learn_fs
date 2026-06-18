# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/StringCodec.java

## Purpose
Provides the canonical UTF-8 string codec for Ozone DB metadata.

## Important APIs, Types, And Functions
`StringCodec.get()` returns a UTF-8 codec with fallback decoding; `getCodecNoFallback()` returns a strict UTF-8 `Codec<String>` implemented by an anonymous `StringCodecBase`.

## Control Flow
The class only constructs singleton codec instances and delegates all encoding/decoding logic to `StringCodecBase`.

## State And Persistence
No mutable state beyond singleton instances. Persistent layout is UTF-8 encoded bytes.

## Dependencies And Integration Points
Depends on `StringCodecBase` and Java `StandardCharsets.UTF_8`. Used for string DB keys/values and delegated codecs.

## Risks
Fallback decoding can preserve compatibility with older data but may hide malformed UTF-8. Callers needing corruption detection should use the no-fallback codec.

## Test Signals
Tests should cover ASCII, multibyte UTF-8, malformed bytes with fallback and no-fallback codecs, and `CodecBuffer` heap/direct round trips.
