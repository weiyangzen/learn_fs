# File Research: sources/virtualization/nbdkit/server/test-public.c

This standalone unit test file provides minimal stubs for server globals and functions, then tests selected public parsing and password APIs. `nbdkit_error` only records that an error was reported, allowing tests to verify both return values and diagnostic behavior.

Covered tests include `nbdkit_parse_size` using shared human-size cases, `nbdkit_parse_probability` with invalid strings, infinities/NaNs, plain numbers, percentages, and `N:M` / `N/M` ratios, and `nbdkit_parse_delay` with seconds, milliseconds, microseconds including `μs`, and nanoseconds.

Integer parsing tests cover signed and unsigned variants from native `int` through 8/16/32/64-bit fixed-width types. They validate decimal, hexadecimal, octal, signs, boundary values, overflow, malformed tokens, trailing garbage, floats, commas, and rejection of negative values for unsigned parsers.

Password tests cover failure on missing files, direct password strings, `+FILE` password file reads, and on non-Windows `-FD` descriptor reads. The test notes that stdin password reading is not covered because it would require a pty. `main` runs all test groups and returns success only if all pass.
