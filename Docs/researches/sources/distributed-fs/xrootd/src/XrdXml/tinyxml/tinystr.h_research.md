# sources/distributed-fs/xrootd/src/XrdXml/tinyxml/tinystr.h

## Purpose

This header defines TinyXML's minimal string and output-stream substitutes for builds without dependable STL support.

## Important APIs, Types, and Functions

- `TiXmlString`: small subset of `std::string` with constructors, assignment, append, `c_str`, `data`, `length`, `capacity`, `find`, `clear`, `reserve`, and comparison operators.
- `TiXmlOutStream`: `TiXmlString` subclass with `operator<<` for TinyXML output accumulation.
- `TIXML_EXPLICIT`: portability macro for older compilers.

## Control Flow

The class wraps a mutable `Rep` structure with size, capacity, and inline storage. Empty strings share `nullrep_`; non-empty strings allocate a buffer. Mutating operations call `assign`, `append`, `reserve`, or `clear`, with comparisons delegated to `strcmp`.

## State and Persistence Behavior

String contents are heap-resident unless empty. Copy construction and assignment make independent buffers. `operator[]` returns a non-const reference even from a const method, reflecting the older TinyXML API style.

## Dependencies and Integration Points

The header is active only when `TIXML_USE_STL` is not defined. `tinyxml.h` uses it as `TIXML_STRING`, and all TinyXML parser/DOM code is built against that typedef.

## Risks

- Not a complete or standards-compatible `std::string`; callers must not assume STL semantics.
- Indexing relies on `assert` and has no runtime bounds checks in release builds.
- C-string operations require null-terminated input.
- The unusual allocation layout can be fragile with sanitizers or exotic allocators.

## Test Signals

Compile TinyXML in non-STL mode, run parser load/save tests, and directly test `TiXmlString` copy, clear, reserve, find, comparisons, and `TiXmlOutStream` append behavior.
