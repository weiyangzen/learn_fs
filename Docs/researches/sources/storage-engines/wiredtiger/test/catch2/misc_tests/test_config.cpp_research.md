# sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_config.cpp

## Purpose
Tests decimal integer parsing for WiredTiger config values, including boundaries, overflow/underflow, length-limited input, whitespace, signs, and stopping at non-digits.

## Important APIs, Types, And Functions
The test directly calls `__wti_config_parse_dec(const char *, size_t, char **)` and checks parsed `int64_t`, `errno`, and `endptr`.

## Control Flow
Sections cover no conversion, exact `INT64_MAX/MIN`, one-less-than-boundaries, out-of-range positive/negative/long values, limited length, non-digit stops, leading blanks, explicit positive/negative signs, and signed zero.

## State And Persistence Behavior
No persistent state. `errno` is explicitly reset for range tests and expected to report `ERANGE`.

## Dependencies And Integration Points
Depends on `wiredtiger.h`, `wt_internal.h`, and C string/errno behavior. It validates parser semantics used by broader config handling.

## Risks And Edge Cases
The key risks are overflow clamping, underflow clamping, `endptr` placement under bounded length, and treating whitespace/signs consistently.

## Test Signals
Expected parsed value, `errno`, and `endptr` position are asserted in each section.
