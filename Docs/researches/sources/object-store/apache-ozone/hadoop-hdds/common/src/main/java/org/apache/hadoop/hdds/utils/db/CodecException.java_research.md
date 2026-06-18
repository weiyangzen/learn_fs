# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/CodecException.java

## Purpose
Typed checked exception for codec serialization and deserialization failures.

## Important APIs, Types, And Functions
`CodecException` extends `IOException` and provides default, message, and message-plus-cause constructors.

## Control Flow
No custom logic; it is constructed and thrown by codec implementations and interface defaults.

## State And Persistence
No persistent state beyond standard exception message and cause.

## Dependencies And Integration Points
Used by `Codec`, `DelegatedCodec`, protobuf codecs, and string codec paths so callers can treat codec failures as IO-level DB failures.

## Risks
Because it extends `IOException`, broad IO handlers may hide data-corruption distinctions unless logs preserve context.

## Test Signals
Codec tests should assert `CodecException` wrapping for invalid bytes, malformed strings, and protobuf parse errors.
