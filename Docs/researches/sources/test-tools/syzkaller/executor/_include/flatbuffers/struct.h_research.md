# sources/test-tools/syzkaller/executor/_include/flatbuffers/struct.h

## Purpose

`struct.h` defines the FlatBuffers runtime `Struct` view type. Structs are fixed-layout inline records without vtables, optional fields, or forward/backward-compatible field evolution.

## Important APIs, Types, and Functions

`class Struct` provides `GetField<T>(uoffset_t)`, `GetStruct<T>(uoffset_t)`, and const/mutable `GetAddressOf(uoffset_t)`. Constructors, copy constructor, and assignment are private because instances are obtained only by pointing into existing buffer data.

## Control Flow

`GetField` reads a scalar at a fixed byte offset using `ReadScalar<T>`. `GetStruct` reinterpret-casts the address at an offset to a nested struct type. `GetAddressOf` returns a raw pointer to the byte offset for reflection or mutation.

## State and Persistence Behavior

`Struct` is a non-owning view over serialized memory and contains a one-byte placeholder array to model flexible inline storage. It is not normally constructed as a C++ object.

## Dependencies and Integration Points

It includes `flatbuffers/base.h`. It is used by generated struct accessors, `Table::GetStruct`, and reflection helpers.

## Risks and Edge Cases

There is no bounds checking. Offsets must come from generated code or trusted reflection metadata, and buffers should be verified before access. Struct schema evolution is limited because all fields are always present at fixed offsets.

## Test Signals

Tests should verify generated struct accessors, nested struct reads, reflection struct access, and verifier coverage for struct alignment and inline size.
