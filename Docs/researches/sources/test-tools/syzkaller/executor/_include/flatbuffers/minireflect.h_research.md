# sources/test-tools/syzkaller/executor/_include/flatbuffers/minireflect.h

## Purpose

`minireflect.h` implements lightweight runtime reflection over generated `TypeTable` metadata. It can iterate tables, structs, vectors, arrays, unions, scalar fields, enum names, and produce compact JSON-like text without loading a full reflection schema.

## Important APIs, Types, and Functions

`IterationVisitor` is the callback interface for sequences, fields, scalar values, strings, unknown values, vectors, and elements. `InlineSize`, `LookupEnum`, and `EnumName` support traversal. `IterateValue`, `IterateObject`, and `IterateFlatBuffer` perform reflection. `ToStringVisitor` and `FlatBufferToString` implement textual output.

## Control Flow

`IterateFlatBuffer` obtains the root pointer and calls `IterateObject`. `IterateObject` walks `type_table->num_elems`, resolves each field type, repetition, type reference, name, and address, then emits field and value callbacks. Repeated table fields dereference FlatBuffers vectors; repeated struct fields use fixed array sizes. `IterateValue` decodes scalars, follows offsets to strings/tables, recurses into nested objects, and handles unions using the preceding union type value or type vector element.

## State and Persistence Behavior

Traversal is stateless apart from visitor-owned data. `ToStringVisitor` stores output, delimiter, quoting, indentation, and vector delimiter state. Reflected object pointers are non-owning views into an existing buffer.

## Dependencies and Integration Points

The header depends on `flatbuffers/flatbuffers.h` and `flatbuffers/util.h`. It integrates with generated code emitted with `--reflect-types` or `--reflect-names`; callers pass the generated root `TypeTable`.

## Risks and Edge Cases

Mini-reflection trusts generated type tables and buffer shape; it does not replace verifier checks for untrusted input. Union handling depends on previous type fields. Without reflected names, output omits field names and enum names. `InlineSize` asserts for unsupported types and depends on correct struct byte sizes.

## Test Signals

Tests should compare `FlatBufferToString` for scalar, enum, nested table, struct, vector, array, and union fields, and assert visitor callback order and absent-field behavior. Verifier tests should precede mini-reflection on external data.
