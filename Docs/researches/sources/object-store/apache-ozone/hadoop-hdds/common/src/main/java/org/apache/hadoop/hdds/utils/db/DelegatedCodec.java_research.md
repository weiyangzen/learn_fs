# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/DelegatedCodec.java

## Purpose
Builds a codec for type `T` by converting to and from a delegate codec type.

## Important APIs, Types, And Functions
Constructor inputs are delegate `Codec<DELEGATE>`, forward conversion, backward conversion, target class, and `CopyType`. Methods forward buffer and byte-array serialization through the delegate. `decodeOnly` builds codecs without backward conversion. `CopyType` supports `DEEP`, `SHALLOW`, and `UNSUPPORTED`.

## Control Flow
Serialization applies `backward` then delegate encoding. Deserialization delegates then applies `forward`. `copyObject()` returns the same object for shallow, throws for unsupported, calls `CopyObject.copyObject()` when available, or deep-copies by delegate copy plus forward/backward conversion.

## State And Persistence
State is immutable conversion configuration. Persisted layout is exactly the delegate codec layout.

## Dependencies And Integration Points
Depends on Ratis `CheckedFunction` and `JavaUtils`, and is widely useful for wrappers around protobuf, strings, or primitive keys.

## Risks
Forward/backward functions must be inverse-compatible or persisted data becomes lossy. `decodeOnly` cannot serialize and will fail late if used for writes. Deep-copy error wrapping converts `CodecException` to `IllegalStateException`.

## Test Signals
Round-trip tests should cover byte-array and buffer paths, all copy types, `CopyObject` implementations, and decode-only failure on serialization.
