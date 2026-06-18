# File Research: sources/os/bsd/freebsd-src/sbin/dhclient/tests/fake.c

## Purpose
Provides test doubles for dhclient fatal/logging and packet-dispatch functions used by the C unit test.

## Main Elements
- `error()` and `warning()`: print formatted output then `longjmp(env, 1)` so tests can assert failure paths.
- `note()` and `parse_warn()`: print formatted messages and return.
- Empty `bootp()` and `dhcp()` stubs.
- Defines `warnings_occurred`.

## Dependencies And Integration
Linked into `option-domain-search_test` in place of production logging and dispatch functions. Uses external `jmp_buf env` from the test file.

## Risk Notes
`warning()` longjmps, unlike production `warning()` which returns. Tests are intentionally structured around this behavior to detect invalid option cases.
