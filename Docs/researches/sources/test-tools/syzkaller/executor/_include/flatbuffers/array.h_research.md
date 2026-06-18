# sources/test-tools/syzkaller/executor/_include/flatbuffers/array.h Research

## Purpose
This vendored FlatBuffers header provides `flatbuffers::Array<T, length>` accessors for fixed-size arrays embedded in serialized structs. In syzkaller it lives under the executor include tree and supports generated/embedded FlatBuffers use without depending on a system installation.

## Important APIs, types, and functions
- Main surface: `Get`, `operator[]`, iterators, `GetEnum`, `Mutate`, `CopyFromSpan`, `make_span`, byte spans, and raw cast helpers.
- Direct includes observed: #include <cstdint>, #include <memory>, #include "flatbuffers/base.h", #include "flatbuffers/stl_emulation.h", #include "flatbuffers/vector.h".
- The file is header-only or declaration-only and participates in the `flatbuffers` or `flexbuffers` namespace API surface.

## Control flow
Control flow is mostly inline/template driven. Callers instantiate templates or call inline helpers; generated FlatBuffers code and builder/parser code compose these primitives. Assertions guard invalid construction order, bounds, alignment, or unsupported operations, while verifier-facing paths return booleans rather than throwing.

## State and persistence
State is either caller-owned serialized memory, builder-owned downward-growing buffers, allocator-owned heap regions, or generator/parser option structures. No independent persistent storage is created by this header, except where abstractions such as file managers or compiler options are implemented elsewhere.

## Dependencies and integration points
Integrates with neighboring FlatBuffers headers in the same vendored include tree and with generated code produced from schemas. In the executor context, ABI stability, endian conversion, allocator behavior, and verifier correctness are more important than application-level business logic.

## Risks and edge cases
- Key risks: endianness, aliasing, bounds asserts, raw casts, and mutation of serialized data.
- Many helpers rely on `FLATBUFFERS_ASSERT`; release builds may not stop misuse.
- Pointer reinterpretation, raw buffer offsets, and in-place mutation require validated buffers and correct lifetimes.
- Because this is vendored third-party API surface, local changes can desynchronize generated code expectations.

## Test signals
Useful validation is compiling executor/generated FlatBuffers consumers, running upstream FlatBuffers unit tests where available, and verifier tests over malformed buffers. This research pass read the header directly and did not run C++ tests.
