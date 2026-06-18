# File Research: sources/os/linux/linux/mm/gup_test.h

## Purpose

`gup_test.h` defines the userspace ABI for the debugfs GUP test driver implemented by `gup_test.c`. It contains ioctl numbers, flag constants, and the fixed-layout structures copied between userspace and the kernel.

## Ioctl Definitions

The header reserves ioctl command type `'g'` for:

- `GUP_FAST_BENCHMARK`
- `PIN_FAST_BENCHMARK`
- `PIN_LONGTERM_BENCHMARK`
- `GUP_BASIC_TEST`
- `PIN_BASIC_TEST`
- `DUMP_USER_PAGES_TEST`
- `PIN_LONGTERM_TEST_START`
- `PIN_LONGTERM_TEST_STOP`
- `PIN_LONGTERM_TEST_READ`

The benchmark and basic test ioctls use `_IOWR()` because the kernel both reads test parameters and writes timing/results back. `PIN_LONGTERM_TEST_START` and `PIN_LONGTERM_TEST_READ` use `_IOW()`, while `PIN_LONGTERM_TEST_STOP` carries no payload.

## Data Structures

`struct gup_test` contains:

- `get_delta_usec` and `put_delta_usec` result fields.
- `addr` and `size` describing the user virtual range.
- `nr_pages_per_call` controlling chunk size for repeated GUP/PUP calls.
- `gup_flags` passed through to the selected API after kernel validation in `gup.c`.
- `test_flags` for test-specific behavior.
- `which_pages[8]`, a 1-based list of page indices for dump tests.

`struct pin_longterm_test` contains:

- `addr`
- `size`
- `flags`

Supported long-term flags are `PIN_LONGTERM_TEST_FLAG_USE_WRITE` and `PIN_LONGTERM_TEST_FLAG_USE_FAST`.

## ABI Notes

All ABI-sized fields use fixed-width Linux integer types. `GUP_TEST_MAX_PAGES_TO_DUMP` is fixed at 8, and zero entries in `which_pages[]` mean "do nothing". The header is tightly coupled to `gup_test.c`; changing structure layout or ioctl numbers would affect userspace tests.
