# sources/storage-engines/foundationdb/bindings/c/symbolify.py

## Purpose
`symbolify.py` generates an Apple `exported_symbols_list` file by extracting exported `fdb_` function names from C API headers.

## Important APIs, Types, And Functions
- Regex `^DLLEXPORT[^(]*(fdb_[^(]*)[(].*$` finds exported `fdb_` function declarations.
- CLI arguments are one or more header files followed by the output symbols file.
- Output symbols are prefixed with `_`, sorted, and written one per line.

## Control Flow
When run as a script, it reads all header files, accumulates matching symbols in a set, sorts them, and writes the output file with a trailing newline.

## State And Persistence Behavior
No runtime state exists. The generated symbols file is a build artifact consumed by the Apple linker.

## Dependencies And Integration Points
CMake invokes this script on Apple with `foundationdb/fdb_c.h` and `foundationdb/fdb_c_internal.h`, then passes the generated file through `-exported_symbols_list`.

## Risks And Edge Cases
The regex requires declarations beginning with `DLLEXPORT`; formatting changes or macro indirection could omit symbols. It only emits `fdb_` names, so non-`fdb_` exported APIs would need script changes.

## Test Signals
Apple build/link success verifies symbol extraction. Missing symbols would surface as runtime link failures or failed C API tests on Apple.
