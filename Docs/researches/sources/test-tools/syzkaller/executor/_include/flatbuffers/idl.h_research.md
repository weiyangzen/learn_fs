# sources/test-tools/syzkaller/executor/_include/flatbuffers/idl.h

## Purpose

`idl.h` defines the in-memory schema model, parser interface, generator options, JSON/text conversion hooks, and gRPC generator declarations for FlatBuffers IDL. It is the shared declaration surface used by schema parsing, binary reflection serialization, JSON parsing, FlexBuffers parsing, and code generators.

## Important APIs, Types, and Functions

The file defines `BaseType` through macros and helpers such as `IsScalar`, `IsInteger`, `IsFloat`, `IsVector`, `SizeOf`, `TypeName`, and `StringOf`. The schema model includes `Type`, `Value`, `SymbolTable<T>`, `Namespace`, `Definition`, `FieldDef`, `StructDef`, `EnumVal`, `EnumDef`, `RPCCall`, `ServiceDef`, and `IncludedFile`. `IDLOptions` contains parser/generator behavior for languages, JSON, binary schema emission, proto mode, optional scalars, object API, TypeScript, Rust, Swift, C#, Python, and 64-bit/vector features. `ParserState`, `CheckedError`, and `Parser` form the parser API. Utility declarations include `GenTextFromTable`, `GenText`, `GenTextFile`, and gRPC generator entry points.

## Control Flow

`Parse` and `ParseJson` initialize state and delegate to private recursive-descent helpers for tokens, namespacing, types, fields, values, tables, vectors, arrays, nested FlatBuffers, metadata, hashes, declarations, services, proto declarations, includes, and JSON. Definitions accumulate in insertion-preserving `SymbolTable`s. `Serialize` converts definitions into binary reflection data in `builder_`; `Deserialize` reconstructs parser definitions from `reflection::Schema`. `ParseFlexBuffer` writes dynamic values into a supplied `flexbuffers::Builder`.

## State and Persistence Behavior

`Parser` owns namespaces, type/struct/enum/service symbol tables, `FlatBufferBuilder builder_`, `flexbuffers::Builder flex_builder_`, root pointers, file identifiers/extensions, include maps, native include lists, known attributes, options, warning/error flags, advanced feature flags, current file, source pointer, field stack, string cache, anonymous counter, and recursion counter. `SymbolTable` owns allocated definitions. No direct persistence is implemented here, but implementation files load schema files and emit builder buffers.

## Dependencies and Integration Points

It depends on `base.h`, `flatbuffers.h`, `flexbuffers.h`, `hash.h`, and `reflection.h`. It connects the parser, binary schema reflection, text generation, FlexBuffers generation, proto compatibility parsing, language generators, and `registry.h`.

## Risks and Edge Cases

Parser state is broad and mutable, so stale state, namespace ownership, include resolution, and recursive depth are key risks. `FLATBUFFERS_MAX_PARSING_DEPTH` defaults to 64. Feature gates for unions, arrays, optional scalars, defaults, 64-bit offsets, and union underlying types must match generator support. `CheckedError` asserts when ignored. `SymbolTable::Add` preserves duplicate insertion in `vec` while reporting duplicate via return value, so callers must enforce uniqueness.

## Test Signals

Strong tests cover schema parsing, JSON parsing, includes, namespaces, unions, arrays, proto mode, attributes, optional scalars, 64-bit offsets, binary schema round trips, conformance, depth limits, duplicate fields/enums, and `ParseFlexBuffer` output.
