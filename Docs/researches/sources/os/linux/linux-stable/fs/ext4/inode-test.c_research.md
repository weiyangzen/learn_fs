# File Research: sources/os/linux/linux-stable/fs/ext4/inode-test.c

## Purpose

KUnit tests for ext4 inode timestamp decoding. The file verifies that `ext4_decode_extra_time()` correctly reconstructs seconds and nanoseconds from the legacy 32-bit timestamp field plus ext4 extra timestamp bits.

## Test Data

The `timestamp_expectation` table covers timestamp boundary cases described by ext4 inode timestamp documentation:

- Negative 32-bit timestamp range without extra seconds bits: 1901 through 1969.
- Nonnegative 32-bit timestamp range without extra seconds bits: 1970 through 2038.
- Extra seconds bit combinations extending representable timestamps beyond 2038.
- High/low extra-bit combinations through dates around 2446.
- Nanosecond decoding, including `1 ns` and maximum 30-bit nanosecond value.

## Main Helpers

- `get_32bit_time()` constructs either the lower or upper bound of a signed 32-bit timestamp, based on whether the most significant bit is set.
- `timestamp_expectation_to_desc()` gives each KUnit parameter a readable case name.
- `KUNIT_ARRAY_PARAM(ext4_inode, ...)` turns the static table into KUnit parameters.

## Main Test

`inode_test_xtimestamp_decoding()`:

- Reads one `timestamp_expectation` from `test->param_value`.
- Calls `ext4_decode_extra_time(cpu_to_le32(base_time), cpu_to_le32(extra_bits))`.
- Asserts both `tv_sec` and `tv_nsec` match the expected values.
- Emits descriptive case information on failure.

## Test Registration

- Defines `ext4_inode_test_cases` with `KUNIT_CASE_PARAM`.
- Registers `ext4_inode_test_suite` named `ext4_inode_test`.
- Module metadata declares GPL v2 licensing.

## Coverage Notes

This test is narrowly focused on timestamp decode arithmetic. It does not exercise inode I/O, checksum validation, timestamp encoding, or mount/runtime integration.
