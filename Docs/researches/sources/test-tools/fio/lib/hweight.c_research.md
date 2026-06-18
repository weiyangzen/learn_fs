# sources/test-tools/fio/lib/hweight.c

Purpose: implements Hamming weight/popcount helpers for fio bit masks.

Important APIs/functions: functions declared in `hweight.h`, including 8/32/64-bit weights. The implementation uses standard bit-counting masks and shifts rather than platform intrinsics.

Control flow/state: pure arithmetic; no allocation, global state, or side effects.

Dependencies/integration: includes only `hweight.h`. Used by bitmap/stat code that needs portable bit counts.

Risks/test signals: tests should cover zero, all-ones, alternating masks, and high-bit-only values for each width. Performance is predictable but may be lower than compiler builtins on some platforms.
