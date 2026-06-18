# sources/test-tools/fio/t/time-test.c

Purpose: arithmetic exploration and regression test for converting CPU clock ticks to nanoseconds using multiplier/shift strategies, two-stage conversion, seqlock-updated conversion, and native 128-bit arithmetic.

Important APIs and types: conversion modes are encoded in an enum (`CLOCK64_MULT_SHIFT`, `CLOCK64_EMULATE_128`, `CLOCK64_2STAGE`, `CLOCK64_LOCK`, `CLOCK128_MULT_SHIFT`). Core functions are `calc_mult_shift()`, `_get_nsec()`, `get_nsec()`, `update_clock()`, `discontinuity()`, and `test_clock()`. It uses fio's `lib/seqlock.h` for the lock-based mode.

Control flow: `main()` allocates a large nanosecond scratch array, then calls `test_clock()` for `CLOCK64_LOCK` across several cycle-per-usec frequencies and expected tick/nsec deltas. `test_clock()` computes multipliers and shifts, checks conversion at maximum and representative times, and can run discontinuity scans when not in fast mode. In the current main path, fast tests are enabled, so full billion-entry scans are skipped.

State and persistence: global conversion parameters, seqlock state, and scratch memory are updated in-process. No files are read or written.

Dependencies and integration points: depends on a compiler supporting `__uint128_t` for the 128-bit path, fio seqlock helpers, and enough memory to allocate `LEN * sizeof(unsigned long long)` even though fast mode does not heavily use it. It is an auxiliary C test/tool rather than registered in the shown umbrella manifest.

Risks and test signals: the emulated 128-bit multiply/divide helpers are explicitly not implemented, so that mode is unsafe if exercised. The huge allocation can be wasteful. Assertions enforce expected continuity constraints. Success is normal exit after printed conversion diagnostics and no assertion failures.
