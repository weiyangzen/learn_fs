# sources/distributed-fs/xrootd/src/XrdXml/tinyxml/tinystr.cpp

## Purpose

This file implements TinyXML's lightweight `TiXmlString` class when `TIXML_USE_STL` is not defined.

## Important APIs, Types, and Functions

- `TiXmlString::npos`: sentinel for failed finds.
- `TiXmlString::nullrep_`: shared empty representation.
- `reserve`, `assign`, and `append`: manage string capacity and content.
- Non-member `operator+` overloads for `TiXmlString` combinations with other `TiXmlString` or C strings.

## Control Flow

`reserve` grows capacity by allocating a temporary string with requested capacity, copying existing bytes, and swapping representations. `assign` either reallocates when capacity is too small or too large relative to new content, or reuses the buffer with `memmove`. `append` grows capacity using `newsize + capacity()` and appends to the current finish pointer.

## State and Persistence Behavior

Each string owns a `Rep` buffer except empty strings, which point at the static `nullrep_`. The implementation uses an `int[]` allocation cast to `Rep *` for alignment portability. All state is in memory.

## Dependencies and Integration Points

It includes `tinystr.h` and is compiled only in non-STL TinyXML mode. `tinyxml.h` maps `TIXML_STRING` to `TiXmlString` unless `TIXML_USE_STL` is enabled.

## Risks

- Assumes non-null C strings in constructors/operators.
- Capacity growth and shrink heuristics are custom and old; overflow is theoretically possible for extreme sizes.
- Uses raw `new[]`, casts, `memmove`, and no exception handling beyond normal C++ allocation behavior.

## Test Signals

Tests should cover empty-string sharing, assign shorter/longer values, append after reserve, concatenation operators, self-overlap safety through `memmove`, and builds with and without `TIXML_USE_STL`.
