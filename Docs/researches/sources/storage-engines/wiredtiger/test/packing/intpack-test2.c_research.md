# sources/storage-engines/wiredtiger/test/packing/intpack-test2.c

## Purpose
This small diagnostic test prints the byte encodings for positive and negative powers of two using WiredTiger variable-length integer packing. It is useful for inspecting encoding shape across magnitude boundaries.

## Important APIs, Types, and Functions
The file uses `__wt_library_init`, `__wt_vpack_uint`, `__wt_vpack_int`, `WT_INTPACK64_MAXSIZE`, and test utility assertions. The only function is `main`.

## Control Flow
`main` initializes a fixed buffer, then iterates `i` from 1 up to but not including `1LL << 60`, doubling each time. For each value, it packs the unsigned value, asserts the encoded length is within the maximum, prints the decimal value and hex bytes, then packs and prints the corresponding negative signed value.

## State, Persistence, and Integration
The test is in-memory and produces stdout as its main diagnostic artifact. It does not unpack and verify values, so it complements rather than replaces round-trip tests. It depends on internal packing APIs and the common test utility initialization path.

## Risks and Test Signals
The file is mainly observational. It can expose unexpected encoding length or byte changes for powers of two, but because it does not decode the result its automated correctness signal is limited to pack return codes and max-size assertions. It is not registered by the local packing CMake file, so routine CTest coverage may not include it unless another build path does.
