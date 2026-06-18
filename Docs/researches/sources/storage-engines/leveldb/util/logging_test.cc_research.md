# sources/storage-engines/leveldb/util/logging_test.cc

## Purpose
Tests the decimal formatting and parsing behavior declared in `util/logging.h`. The file focuses on correctness around ordinary values, `uint64_t` limits, suffix preservation, overflow rejection, and no-digit rejection.

## Important APIs, Types, And Functions
The tests use `NumberToString`, `ConsumeDecimalNumber`, `Slice`, and GoogleTest assertions. Helper functions `ConsumeDecimalNumberRoundtripTest`, `ConsumeDecimalNumberOverflowTest`, and `ConsumeDecimalNumberNoDigitsTest` reduce repeated setup.

## Control Flow
Roundtrip tests format a number, append optional padding, parse from a copied `Slice`, then verify the numeric result and remaining suffix length. Overflow tests assert parsing returns false for values just above `UINT64_MAX` and all-nines input. No-digit tests assert failure and that the slice pointer and size remain unchanged.

## State And Persistence Behavior
The tests create only local strings and slices. They do not touch LevelDB databases, environment files, or global state.

## Dependencies And Integration Points
The file integrates the logging implementation with GoogleTest. It assumes `std::numeric_limits<uint64_t>::max()` equals `18446744073709551615U` through static assertions, so the tests document the expected platform width.

## Risks And Edge Cases
Escaped string formatting is not tested here. Overflow tests do not assert that the input slice remains unchanged, matching the looser header contract. Padding includes printable text and embedded NULs, which is useful for slice-length behavior.

## Test Signals
Failures in this file indicate regressions in decimal formatting, parse advancement, overflow checks, or no-digit handling. The near-maximum loop gives dense coverage of the most error-prone overflow boundary.
