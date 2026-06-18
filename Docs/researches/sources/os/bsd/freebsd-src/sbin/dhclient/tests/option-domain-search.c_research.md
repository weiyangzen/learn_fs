# File Research: sources/os/bsd/freebsd-src/sbin/dhclient/tests/option-domain-search.c

## Purpose
Unit-tests domain-search option expansion and lease-date parsing.

## Main Elements
- Domain-search tests:
  - No option present.
  - One and two valid domains.
  - Truncated labels/domains.
  - Compressed names using RFC 1035 pointers.
  - Invalid self/forward/truncated pointers.
  - Multiple compressed domains.
- `parse_date_helper()` writes a temporary lease-date string, runs lexer setup, calls `parse_date()`, and compares timestamp.
- `parse_date_valid()` verifies a 2024 timestamp and, except on i386, a 2091 timestamp.
- `main()` runs all tests and aborts on unexpected behavior.

## Dependencies And Integration
Links production `options.c`, `parse.c`, lexer/config helpers, tables, allocation, hash, conversion, tree, and `fake.c`. Uses `setjmp` to catch expected parser warnings/errors.

## Risk Notes
The test writes `/tmp/dhclient.test` directly. It covers important compression-pointer safety cases for network-provided option 119.
