# sources/storage-engines/wiredtiger/test/packing/intpack-test.c

## Purpose
This is a stress/performance-style round-trip test for WiredTiger variable-length unsigned integer packing. It repeatedly packs and unpacks powers of two and verifies that values survive encoding.

## Important APIs, Types, and Functions
The file includes `test_util.h`, initializes the WT library with `__wt_library_init`, and uses `__wt_vpack_uint`, `__wt_vunpack_uint`, `WT_INTPACK64_MAXSIZE`, `testutil_check`, and `testutil_assert`. The only test body is `main`.

## Control Flow
`main` initializes a buffer, then loops ten million outer iterations. For each iteration, it walks shift values from 0 to 45 in steps of 5, computes `1ULL << s`, packs it, records encoded length, asserts that length is within the max size, unpacks it, and asserts equality. It counts calls and prints the total.

## State, Persistence, and Integration
The test is entirely in-memory and has no persistent state. It uses an oversized buffer initialized to `0xff` to avoid compiler uninitialized warnings and to provide room beyond the maximum pack size. A disabled `#else` block contains a `memmove` baseline useful for local performance comparison but not active in normal test builds.

## Risks and Test Signals
Risk coverage is narrow but high-volume: it detects regressions in unsigned varint round-trip correctness for several magnitude classes. It does not test signed packing, malformed inputs, or full boundary coverage. Signals are assertion failures, `__wt_*` return codes, encoded length limits, and the printed number of calls.
