# sources/test-tools/syzkaller/executor/_include/flatbuffers/reflection.h

## Purpose

`reflection.h` provides higher-level helpers for binary schema reflection. It uses `reflection::Schema` metadata to inspect, read, write, resize, copy, and verify arbitrary FlatBuffers without generated accessors.

## Important APIs, Types, and Functions

Getter helpers include type classifiers, `GetTypeSize`, `GetTypeSizeInline`, `GetAnyRoot`, `GetField*`, `GetAnyValue*`, `GetAnyField*`, vector element helpers, generic pointer/address helpers, and `ForAllFields`. Mutation helpers include `SetField`, `SetAnyValue*`, `SetAnyField*`, `SetAnyVectorElem*`, `pointer_inside_vector`, `piv`, `GetUnionType`, `SetString`, `ResizeAnyVector`, `ResizeVector`, `AddFlatBuffer`, and `SetFieldT`. Copy/verify declarations are `CopyTable`, `Verify`, and `VerifySizePrefixed`.

## Control Flow

Read helpers use reflected field offsets and base types to dispatch reads from tables, structs, vectors, and defaults. Pointer helpers decode relative offsets for strings, tables, and vectors. Setters locate existing fields or vector elements and write through base-type dispatch. Resizing helpers mutate a `std::vector<uint8_t>` so internal offsets can be adjusted. `AddFlatBuffer` appends new serialized data and returns a pointer suitable for offset mutation.

## State and Persistence Behavior

Most helpers are stateless and operate on caller-owned buffers. Resizing and string helpers mutate a `std::vector<uint8_t>` in place and can invalidate pointers; `pointer_inside_vector` stores offsets relative to vector data to survive resize.

## Dependencies and Integration Points

The header includes `reflection_generated.h` and depends on `Table`, `Struct`, `VectorOfAny`, `FlatBufferBuilder`, and `Verifier`. It consumes binary schemas emitted by `flatc --schema` or `Parser::Serialize`.

## Risks and Edge Cases

Many helpers perform little type checking and rely on correct reflection metadata. Wrong offset width, wrong field type, or stale pointers after resize can corrupt buffers. `GetFieldStruct` cannot fully distinguish table versus struct without schema context. `CopyTable` duplicates DAG-shaped tables as trees.

## Test Signals

Tests should cover reflection reads/writes for all scalar widths, strings, vectors, structs, tables, unions, defaults, optional fields, size-prefixed buffers, 64-bit offsets, reflection verification parity with generated verifiers, and pointer invalidation during mutation.
