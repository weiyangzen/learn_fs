# sources/test-tools/fio/td_error.h

## Purpose
`td_error.h` defines fio's error-type bit ABI for read, write, and verify error handling and declares helper functions implemented in `td_error.c`.

## Important APIs, Types, and Functions
`enum error_type_bit` provides array indexes and bit positions: `ERROR_TYPE_READ_BIT`, `ERROR_TYPE_WRITE_BIT`, `ERROR_TYPE_VERIFY_BIT`, and `ERROR_TYPE_CNT`. `enum error_type` provides bit masks used by options such as `continue_on_error`: `ERROR_TYPE_NONE`, `ERROR_TYPE_READ`, `ERROR_TYPE_WRITE`, `ERROR_TYPE_VERIFY`, and broad `ERROR_TYPE_ANY`. Function declarations expose `td_error_type()`, `td_non_fatal_error()`, and `update_error_count()`.

## Control Flow and State
This header has no runtime control flow. Its state significance is ABI-like: `ERROR_TYPE_CNT` sizes arrays in `thread_options`, while the bit values define persisted option semantics and mask behavior.

## Dependencies and Integration Points
It includes `io_ddir.h` for data direction types and is included by `thread_options.h` and error-handling C files. The enum values must remain consistent with option parsing, packed thread option structures, and network/client/server conversions.

## Risks and Test Signals
Changing enum order or count can break option arrays, packed conversions, and compatibility. `ERROR_TYPE_ANY=0xffff` intentionally exceeds the three current bits. Signals include build failures, option conversion tests, and runtime behavior of `continue_on_error` and `ignore_error`.
