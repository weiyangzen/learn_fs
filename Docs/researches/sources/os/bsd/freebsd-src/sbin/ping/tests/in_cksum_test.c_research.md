# File Research: sources/os/bsd/freebsd-src/sbin/ping/tests/in_cksum_test.c

ATF-C unit tests for the Internet checksum helper.

Key elements:
- Four test cases cover aligned even length, aligned odd length, unaligned even length, and unaligned odd length inputs.
- Each test calls `in_cksum` and asserts expected checksum bytes.
- Registers all test cases through `ATF_TP_ADD_TCS`.

Dependencies:
- Includes `../utils.h`.
- Uses ATF-C and FreeBSD `nitems`.

Research notes:
- The tests explicitly exercise unaligned input by offsetting an aligned byte array by one byte, matching the implementation’s `memcpy`-based unaligned-safe reads.
