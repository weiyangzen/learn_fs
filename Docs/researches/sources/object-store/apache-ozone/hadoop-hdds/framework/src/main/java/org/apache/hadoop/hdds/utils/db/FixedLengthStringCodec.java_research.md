# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/FixedLengthStringCodec.java

## Purpose
`FixedLengthStringCodec` serializes strings with ISO-8859-1 so serialized byte length equals Java string length for supported characters. It is useful for fixed-width key schemas.

## Important APIs and Types
`get()` returns the singleton. Static helpers `string2Bytes` and `bytes2String` delegate to the codec. The class extends `StringCodecBase.WithFallback` with `StandardCharsets.ISO_8859_1`.

## Control Flow and State
The codec is stateless. Encoding errors in `string2Bytes` are converted to `IllegalStateException` through the provided exception factory.

## Persistence, Dependencies, and Integration
It participates in typed DB persistence where fixed byte length matters. Dependencies include `StringCodecBase` and Java charset APIs.

## Risks and Test Signals
Characters outside ISO-8859-1 can trigger fallback/error behavior depending on the base class. Tests should cover ASCII and high Latin-1 round trips, unsupported character behavior, byte-length equality, null handling inherited from the base codec, and ordering implications for keys.
