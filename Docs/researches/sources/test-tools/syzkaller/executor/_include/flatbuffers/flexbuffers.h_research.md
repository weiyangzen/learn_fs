# sources/test-tools/syzkaller/executor/_include/flatbuffers/flexbuffers.h

## Purpose

`flexbuffers.h` implements the self-describing FlexBuffers binary format in a header-only form. It provides type tags, compact width selection, readers, writers, JSON-like rendering, in-place scalar/string mutation, map lookup, and structural verification for FlexBuffers buffers.

## Important APIs, Types, and Functions

The core format enums are `BitWidth` and `Type`, with helpers such as `IsInline`, `IsTypedVector`, `IsFixedTypedVector`, `ToTypedVector`, `PackedType`, and scalar helpers `ReadInt64`, `ReadUInt64`, `ReadDouble`, `Indirect`, `WidthU`, `WidthI`, and `WidthF`. Read-side wrappers are `Object`, `Sized`, `String`, `Blob`, `Vector`, `TypedVector`, `FixedTypedVector`, `Map`, and `Reference`. `Reference` exposes type predicates, `As*` conversion methods, `ToString`, and in-place mutation helpers. `Builder` writes values through scalar/key/string/blob appenders, vector/map start/end APIs, typed vectors, sharing flags, `LastValue`, `ReuseValue`, `ForceMinimumBitWidth`, and `Finish`. `Verifier` and free `VerifyBuffer` validate buffers.

## Control Flow

Reading starts at `GetRoot`, which parses backward from final byte width and packed type. `Reference` conversions branch on `type_`; inline scalars read directly, indirect values compute `Indirect()`, vectors synthesize element references, and maps binary-search a sorted key vector. Writing is stack based: scalar calls push `Builder::Value`, strings/keys/blobs write bytes immediately, and `EndVector`/`EndMap` convert a stack range into serialized vectors or maps. `EndMap` sorts key/value pairs, writes a typed key vector, then writes the value vector with key metadata. `Finish` writes the root value, packed type, and root width. Verification mirrors this layout recursively with offset, alignment, depth, vector-count, key terminator, and optional reuse-tracker checks.

## State and Persistence Behavior

`Reference` and wrapper objects are non-owning views into caller-owned memory. Mutations write directly into that memory and only succeed when the new value fits the original encoded width or a replacement string has identical length. `Builder` owns `buf_`, pending `stack_`, key/string pools, duplicate-key state, finish state, sharing flags, and forced minimum bit width. `Clear` resets reusable state but keeps flags. There is no filesystem persistence.

## Dependencies and Integration Points

The header depends on FlatBuffers `base.h` and `util.h` for endian-safe I/O, padding, conversions, escaping, assertions, and traits. It uses STL containers and algorithms. `idl.h` includes it for JSON-like FlexBuffers parsing and `IDLOptions::use_flexbuffers`.

## Risks and Edge Cases

The format is pointer-arithmetic heavy, so untrusted buffers should be verified before reading. `GetRoot` assumes sufficient size; `VerifyBuffer` checks root metadata. Map lookup depends on sorted duplicate-free keys; duplicate keys are only recorded in `has_duplicate_keys_`. Typed vectors require homogeneous supported element types, fixed typed vectors support only scalar lengths 2 through 4, deprecated string vectors are treated as key vectors, and `ScalarVector` asserts when length width exceeds element width. Mutation returns false when width or length constraints are not met.

## Test Signals

Useful tests cover scalar width minimization, vectors/maps, duplicate keys, string/key sharing, mutation, malformed offsets, truncated root metadata, unterminated keys/strings, depth limits, and verifier reuse tracking. In this repo, compilation of vendored FlatBuffers-generated code is the main integration signal.
