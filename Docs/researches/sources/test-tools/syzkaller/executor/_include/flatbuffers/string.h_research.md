# sources/test-tools/syzkaller/executor/_include/flatbuffers/string.h

## Purpose

`string.h` defines the FlatBuffers runtime `String` view type and null-safe string helpers. A FlatBuffers string is a `Vector<char>` with a trailing NUL in serialized memory.

## Important APIs, Types, and Functions

`struct String : public Vector<char>` provides `c_str`, `str`, optional `string_view`, and `operator<`. Free helpers are `GetString`, `GetCstring`, and optional `GetStringView`, each returning an empty value for null input.

## Control Flow

`c_str` returns `Data()` as `const char *`. `str` builds a `std::string` from explicit pointer and size, preserving embedded NUL bytes. `operator<` delegates to `StringLessThan`. Helper functions null-check before calling members.

## State and Persistence Behavior

`String` is a non-owning view over serialized memory. It allocates only when `str()` constructs a `std::string`. `GetCstring(nullptr)` returns a static empty string literal.

## Dependencies and Integration Points

It includes `base.h` and `vector.h`. Generated accessors for string fields return `const String *` and commonly use these helpers for host-string conversion.

## Risks and Edge Cases

`c_str` assumes a valid FlatBuffers trailing NUL; verify untrusted buffers first. The empty literal returned for null must not be mutated. `string_view` depends on `FLATBUFFERS_HAS_STRING_VIEW`. Ordering is FlatBuffers byte/length comparison, not locale-aware comparison.

## Test Signals

Tests should cover null helpers, embedded NUL preservation, string-view length, comparison ordering, and verifier rejection of malformed strings before `c_str` use.
