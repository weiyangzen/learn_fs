# sources/test-tools/fio/t/fuzz/onefile.c

## Purpose
Small standalone driver that reads one input file and passes its bytes to `LLVMFuzzerTestOneInput()`, allowing fuzz targets to be reproduced outside a fuzzer runtime.

## Important APIs, Types, and Functions
Declares the external `LLVMFuzzerTestOneInput()` symbol and implements `main()`. Uses standard C file I/O, `fseek()`, `ftell()`, `malloc()`, and `fread()`.

## Control Flow
`main()` requires exactly one path. It opens the file in binary mode, seeks to the end to determine size, rewinds, allocates an exact-size buffer, reads the entire file, calls the fuzz entry point, frees the buffer, closes the file, and returns zero unless setup/read errors occurred.

## State and Persistence Behavior
No persistent state beyond reading the supplied file. It returns `1` for usage errors and `2` for file/allocation/read failures.

## Dependencies and Integration Points
Designed to link with a fuzz target such as `fuzz_parseini.c`. It is useful for crash minimization and CI reproduction of a specific corpus file.

## Risks
`ftell()` result is cast to `size_t`, so extremely large files or platform-specific `long` limits can be problematic. Empty files allocate zero bytes and then expect `fread(..., size, 1, ...) == 1`, which may reject them.

## Test Signals
The executable should reproduce the same return/crash behavior as the fuzzer entry point for a given corpus file.
