# File Research: sources/os/linux/linux/fs/ext4/inode-test.c

## Purpose

`fs/ext4/inode-test.c` is a KUnit test module for ext4 inode timestamp decoding. It verifies that `ext4_decode_extra_time()` correctly decodes the seconds and nanoseconds portions of ext4 inode timestamps across documented boundary cases.

## Test Coverage

The file defines a table of `struct timestamp_expectation` entries covering:

- negative 32-bit timestamp lower and upper bounds;
- nonnegative 32-bit timestamp lower and upper bounds;
- extra seconds bit 0 set;
- extra seconds bit 1 set;
- both extra seconds bits set;
- nanosecond decoding, including `1 ns` and maximum supported nanoseconds;
- documented date ranges from 1901 through 2446, matching the ext4 inode timestamp documentation.

Important constants:

- `LOWER_MSB_0`, `UPPER_MSB_0`: nonnegative 32-bit timestamp boundaries.
- `LOWER_MSB_1`, `UPPER_MSB_1`: negative 32-bit timestamp boundaries.
- `MAX_NANOSECONDS`: `(1 << 30) - 1`, the 30-bit nanosecond field maximum.
- `CASE_NAME_FORMAT`: assertion diagnostic format for parameterized failures.

## Main Test Flow

- `timestamp_expectation_to_desc()` gives each KUnit parameter a descriptive case name.
- `KUNIT_ARRAY_PARAM(ext4_inode, test_data, timestamp_expectation_to_desc)` creates the parameter generator.
- `get_32bit_time()` builds the low 32-bit timestamp input according to whether the test wants the signed MSB set and lower/upper bound value.
- `inode_test_xtimestamp_decoding()` calls:

  `ext4_decode_extra_time(cpu_to_le32(get_32bit_time(test_param)), cpu_to_le32(test_param->extra_bits))`

  It then asserts both `tv_sec` and `tv_nsec` against expected values with `KUNIT_EXPECT_EQ_MSG()`.

- `ext4_inode_test_cases` registers the parameterized test.
- `ext4_inode_test_suite` names the suite `ext4_inode_test`.
- `kunit_test_suites()` registers the suite as a module-level KUnit test.

## Dependencies and Integration

The file includes:

- `<kunit/test.h>` for KUnit infrastructure;
- `<linux/time64.h>` for `struct timespec64` and `time64_t`;
- `ext4.h` for `ext4_decode_extra_time()` and ext4 timestamp encoding definitions.

It does not instantiate a filesystem, mount ext4, or allocate inodes. This is a pure decode-table unit test.

## Behavior Verified

The test validates that ext4 extra timestamp bits extend the signed 32-bit seconds field into the documented extended timestamp range and preserve nanosecond values from the high bits of the extra timestamp field.

## Notable Risk Areas

- The test is table-driven and focused only on `ext4_decode_extra_time()`. It does not test timestamp encoding, raw inode read/write integration, endianness beyond explicit `cpu_to_le32()` inputs, or filesystem mount behavior.
- It intentionally tests boundary values; regressions in bit placement or sign-extension behavior should produce clear parameterized KUnit failures.
