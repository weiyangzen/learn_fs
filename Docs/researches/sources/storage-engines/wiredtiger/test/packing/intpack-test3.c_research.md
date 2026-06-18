# sources/storage-engines/wiredtiger/test/packing/intpack-test3.c

## Purpose
This C test validates round-trip signed and unsigned WiredTiger variable-length integer packing over dense ranges around important boundaries. It extends coverage beyond simple powers of two by checking values near zero, INT16_MAX, INT32_MAX, INT64_MAX, and successively halved large ranges.

## Important APIs, Types, and Functions
The file declares `test_value` and `test_spread`. `test_value` exercises `__wt_vpack_int`, `__wt_vunpack_int`, `__wt_vpack_uint`, and `__wt_vunpack_uint`, with size checks against `WT_INTPACK64_MAXSIZE`. `test_spread` loops over a contiguous range and calls `test_value`.

## Control Flow
`main` computes a `range` of 1025 and a safe start near `INT64_MAX`, then calls `test_spread` for a large range around zero and for ranges around signed 16-bit, signed 32-bit, and signed 64-bit maxima. It then repeatedly halves the large start value and tests a spread around each point. `test_value` packs/unpacks a signed value and an unsigned cast of the same bit pattern, verifies equality, and verifies the unpack pointer consumed exactly the bytes written.

## State, Persistence, and Integration
The test is in-memory only. Each value gets a fresh buffer initialized to `0xff`, local pointer cursors, and local signed/unsigned variables. It depends on internal integer packing APIs and test utility initialization; `__wt_library_init` is called in `test_value`, so the library is initialized repeatedly during the run.

## Risks and Test Signals
This file targets off-by-one and boundary-class regressions in variable-length integer encodings. Pointer-consumption assertions catch decoders that return the right value but consume the wrong length. A likely defect in the unsigned mismatch check compares `sinput` and `soutput` again instead of checking `uinput` and `uoutput`, reducing automated unsigned verification strength. The file is the registered `test_intpack` source in the packing CMake file, so failures are visible through CTest.
