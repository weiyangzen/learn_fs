# sources/test-tools/syzkaller/executor/_include/flatbuffers/table.h

## Purpose

`table.h` defines the FlatBuffers runtime `Table` view type. Tables are variable-layout objects with vtables, optional fields, defaults, pointer fields, struct fields, mutation helpers, and verification helpers.

## Important APIs, Types, and Functions

`Table` exposes `GetVTable`, `GetOptionalFieldOffset`, `GetField`, `GetPointer`, `GetPointer64`, `GetStruct`, `GetOptional`, `SetField`, `SetPointer`, `GetAddressOf`, `CheckField`, `VerifyTableStart`, `VerifyField`, `VerifyFieldRequired`, `VerifyOffset`, `VerifyOffsetRequired`, `VerifyOffset64`, and `VerifyOffset64Required`. `GetOptional<uint8_t, bool>` is specialized to avoid bool warnings.

## Control Flow

`GetVTable` subtracts the signed vtable offset at the table start. `GetOptionalFieldOffset` checks the vtable size and returns zero for absent or out-of-range fields. Scalar getters return serialized values or defaults. Pointer getters decode relative offsets. Struct getters return inline addresses. Setters mutate existing fields and cannot materialize absent fields, except the default-aware scalar overload can accept unchanged default values for absent fields. Generated verifiers call table-start, field, offset, and required-field helpers.

## State and Persistence Behavior

`Table` is a non-owning view over serialized memory. In-place setters mutate the buffer but cannot add vtable entries. Constructors and assignment are private; instances come from FlatBuffers root or pointer accessors.

## Dependencies and Integration Points

It includes `base.h` and `verifier.h`. It is central to generated table accessors, generated verifiers, `reflection_generated.h`, and schema-driven reflection helpers.

## Risks and Edge Cases

Reading corrupt tables without verification can produce invalid pointers. Using 32-bit pointer helpers on 64-bit offset fields is wrong. In-place mutation cannot create absent fields. `GetAddressOf` returns null for absent fields and must be checked.

## Test Signals

Tests should cover generated accessors for optional/default/required fields, strings, vectors, tables, structs, 64-bit offsets, mutation APIs, truncated vtables, missing required fields, bad offsets, and offset64 cases.
