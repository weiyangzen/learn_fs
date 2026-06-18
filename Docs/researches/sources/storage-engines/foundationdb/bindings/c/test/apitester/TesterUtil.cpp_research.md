# sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterUtil.cpp

## Purpose
Implements common API tester utilities for randomness, byte/value copying, assertions, and temporary files.

## Important APIs, types, and functions
`lowerCase`, `Random::randomInt/randomBool/get`, `print_internal_error`, `copyValueRef`, `copyKeyValueArray`, `copyKeyRangeArray`, and `TmpFile::{create,write,remove}` are the core functions.

## Control flow
Array-copy helpers iterate native FDB result arrays into owned C++ containers. `TmpFile::create` retries randomized names until unused, creates an empty file, and later writes/removes it.

## State and persistence behavior
`Random::get` is thread-local mutable RNG state. `TmpFile` persists a real filesystem file for its lifetime and logs removal failure rather than throwing.

## Dependencies and integration points
Depends on `test/fdb_api.hpp`, filesystem/streams, `fmt`, and C runtime helpers. Used by parser, executor, and workloads.

## Risks and test signals
Copy helpers prevent use-after-free of FDB future buffers. Temp-file leaks or removal errors signal abnormal process/platform behavior.
