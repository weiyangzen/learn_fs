# sources/storage-engines/foundationdb/flow/include/flow/flat_buffers.h

## Purpose
Trait-driven FlatBuffers-compatible serializer for Flow object serialization, covering tables, vectors, unions, structs, dynamic bytes, vtables, and file identifiers.

## Important APIs, Types, And Functions
Public helpers are `save_members`, `load_members`, `read_file_identifier`, and `EnsureTable<T>`. Traits cover scalars, tuples, pairs, vectors/deques/arrays/maps/sets/unordered containers, flat maps, strings, unions, and dynamic-size types. Internals include `RelativeOffset`, `PrecomputeSize`, `WriteToBuffer`, `VTableSet`, `SaveVisitorLambda`, `LoadMember`, `LoadSaveHelper`, and `FakeRoot`.

## Control Flow
Serialization first traverses with `PrecomputeSize` to compute final buffer size, dynamic payload placement, vtables, and offsets. It then traverses with `WriteToBuffer` to copy bytes and fix relative offsets. Loading reads table/vtable offsets, checks field presence, and reconstructs members through traits.

## State And Persistence Behavior
The output buffer is persistent/transmittable serialized data. Vtable caches and scratch vectors are thread-local process state. Root file identifiers support type validation.

## Dependencies And Integration Points
Depends on `FileIdentifier`, `ObjectSerializerTraits`, and Flow serializer conventions. Used by `flow.h` serialization wrappers and the wider RPC/object serialization system.

## Risks And Edge Cases
Nested struct-like structs are unsupported. Union alternatives are capped at 254. Missing fields default-construct, which helps compatibility but can hide unsafe schema drift. Raw serialization bypasses normal table generation.

## Test Signals
Round trips for supported containers, unions, vectors of unions, empty vectors, `vector<bool>`, missing fields, file identifiers, alignment/padding, raw paths, and cross-version RPC/object payloads.
