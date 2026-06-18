# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/StringCodecBase.java

## Purpose
Abstract charset-based implementation for string codecs with strict encoding and optional fallback decoding.

## Important APIs, Types, And Functions
The class stores `Charset`, fixed-length status, and `maxBytesPerChar`. Important methods are `newEncoder`, `newDecoder`, `isFixedLength`, `toCodecBuffer`, `fromCodecBuffer`, `toPersistedFormat`, `fromPersistedFormat`, `string2Bytes`, `decodeNoFallback`, and nested `WithFallback`.

## Control Flow
Encoding computes an upper-bound size, encodes through a `CharsetEncoder` configured to `REPORT` malformed/unmappable input, and either uses exact array size for fixed-width charsets or a heap `CodecBuffer` for variable width. Buffer serialization allocates the upper bound and sets writer index based on actual encoded bytes. Strict decode throws `CodecException`; fallback logs the strict failure then calls `StringUtils.bytes2String`.

## State And Persistence
Immutable codec configuration only. Persistent bytes are determined by the configured charset.

## Dependencies And Integration Points
Used by `StringCodec` and any future charset-specific string codecs. Depends on Java NIO charset APIs, `CodecBuffer`, Ratis preconditions, and HDDS string utilities.

## Risks
The max-bytes-per-char value must be an integer; unusual charsets can throw at construction. Fallback logs can be noisy on corrupt data. `StringUtils.bytes2String` compatibility behavior may not match strict charset semantics.

## Test Signals
Tests should include variable-length UTF-8, malformed byte arrays, size mismatch protection, direct and heap buffers, fallback log paths, and fixed-length charset behavior if a subclass is added.
