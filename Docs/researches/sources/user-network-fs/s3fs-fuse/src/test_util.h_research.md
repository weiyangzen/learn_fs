# sources/user-network-fs/s3fs-fuse/src/test_util.h

## Purpose
Provides lightweight assertion helpers for s3fs C++ unit tests without depending on a test framework.

## Important APIs, Types, And Control Flow
Template `assert_equals` and `assert_nequals` compare generic values and abort with file/line diagnostics. `std::string` specializations also print hex encodings using `s3fs_hex_lower`. `assert_strequals` handles null C strings. `assert_bufequals` compares byte buffers by length and `memcmp`. Macros wrap these functions with `__FILE__` and `__LINE__`.

## State And Persistence
No persistent state. On failure it writes diagnostics to stderr and aborts the process.

## Dependencies And Integration Points
Includes C stdio/stdlib, iostream, string, and `string_util.h` for hex diagnostics. Used by `test_string_util.cpp`, `test_curl_util.cpp`, `test_page_list.cpp`, and likely other unit tests.

## Risks And Test Signals
Abort-based assertions are simple but prevent multiple failures from being reported in one run. Buffer diagnostics construct strings from possibly binary data and may be noisy. The macros are compile-time integration signals for tests that need no external framework.
