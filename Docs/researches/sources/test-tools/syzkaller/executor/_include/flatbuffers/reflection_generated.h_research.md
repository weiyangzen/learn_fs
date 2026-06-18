# sources/test-tools/syzkaller/executor/_include/flatbuffers/reflection_generated.h

## Purpose

`reflection_generated.h` is the generated C++ binding for FlatBuffers' binary schema format. It defines serialized schema tables used by `idl.h` and `reflection.h` to persist and inspect schema metadata.

## Important APIs, Types, and Functions

The header asserts FlatBuffers version `23.5.26`, defines `reflection::BaseType`, `reflection::AdvancedFeatures`, enum name helpers, and generated table types `Type`, `KeyValue`, `EnumVal`, `Enum`, `Field`, `Object`, `RPCCall`, `Service`, `SchemaFile`, and `Schema`. Each table has accessors, vtable constants, key comparison helpers where needed, and `Verify`. Each table also has a builder, `Create*`, and often `Create*Direct`. Root helpers include `GetSchema`, identifier checks, verifier helpers, extension, and finish functions.

## Control Flow

Generated accessors read fields through `Table::GetField` or `GetPointer`. `Verify` methods check table starts, required offsets, nested tables/vectors/strings, scalar alignment, and table end. Builders start a table, add fields, finish, and mark required fields. Direct constructors create strings and sorted vectors before delegating to create functions. Root buffers use identifier `BFBS` and extension `bfbs`.

## State and Persistence Behavior

Generated table objects are non-owning views into FlatBuffers memory. Builder state is local to a referenced `FlatBufferBuilder`. Persisted schema state includes objects, enums, file identifiers/extensions, root table, services, advanced feature mask, and per-file include metadata.

## Dependencies and Integration Points

The header includes `flatbuffers/flatbuffers.h`, is included by `reflection.h`, and is consumed by `idl.h` for parser schema serialization/deserialization.

## Risks and Edge Cases

Manual edits would break generated-code compatibility. Runtime/generator version mismatches fail compilation. Required fields are enforced by builders and verifiers, but invalid buffers can still be hand-built. Sorted-vector lookup depends on using the sorted creation helpers and matching key comparisons.

## Test Signals

Tests should verify parser-produced schema buffers pass `VerifySchemaBuffer`, carry `BFBS`, and round-trip through `GetSchema` and parser deserialization. Accessor tests should inspect objects, fields, enums, services, schema files, advanced features, optional/padding/offset64 metadata, and size-prefixed variants.
