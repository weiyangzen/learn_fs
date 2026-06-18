# sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterUtil.h

## Purpose
Declares shared utilities for API tester code: random generation, errors/asserts, time measurement, FDB result copying, endian conversions, and temp files.

## Important APIs, types, and functions
`Random`, `TesterError`, `ASSERT`, `TimePoint` helpers, `copyValueRef`, `copyKeyValueArray`, `copyKeyRangeArray`, `toInteger`, `toByteString`, and `TmpFile` are the main API surface.

## Control flow
Most functions are inline. Integral conversion asserts exact byte width, then `memcpy`s little-endian payloads.

## State and persistence behavior
`Random` is per-thread nondeterministic state. `TmpFile` owns a filesystem path and removes it on destruction.

## Dependencies and integration points
Includes `test/fdb_api.hpp`, `fmt`, and generated Flow error definitions, making FDB error constants available to tester code.

## Risks and test signals
Nondeterministic seeds can complicate reproduction. The little-endian static assertion protects atomic-operation value encoding on unsupported architectures.
