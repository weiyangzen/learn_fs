# sources/test-tools/syzkaller/executor/_include/flatbuffers/hash.h

## Purpose

`hash.h` provides named FNV-1 and FNV-1a hash implementations used by FlatBuffers schema hash attributes. It supports 16-, 32-, and 64-bit outputs and exposes lookup tables by schema-visible name.

## Important APIs, Types, and Functions

`FnvTraits<T>` supplies FNV prime and offset basis for `uint32_t` and `uint64_t`. `HashFnv1<T>` and `HashFnv1a<T>` consume NUL-terminated strings. `uint16_t` specializations fold the 32-bit hash. `NamedHashFunction<T>` pairs names with function pointers. `kHashFunctions16`, `kHashFunctions32`, `kHashFunctions64`, and `FindHashFunction16/32/64` expose lookup.

## Control Flow

Hashing starts from the offset basis and iterates until NUL. FNV-1 multiplies then XORs each byte; FNV-1a XORs then multiplies. Lookup functions linearly scan the static table for the requested width and return a function pointer or `nullptr`.

## State and Persistence Behavior

The header is stateless aside from static const tables. It does not cache results and treats inputs as C strings, so embedded NUL bytes terminate hashing.

## Dependencies and Integration Points

It depends on `<cstdint>`, `<cstring>`, and `flatbuffers/flatbuffers.h`. `idl.h` includes it so parser code can resolve `hash` attributes.

## Risks and Edge Cases

The hashes are non-cryptographic. The 16-bit variants have high collision probability. Passing null or non-NUL-terminated input is unsafe. Unknown names return `nullptr`, so callers must check.

## Test Signals

Tests should compare known FNV vectors, verify 16-bit folding, and exercise lookup success/failure. Parser tests using schema `hash` attributes indirectly cover it.
