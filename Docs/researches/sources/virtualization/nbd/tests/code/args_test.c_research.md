# File Research: sources/virtualization/nbd/tests/code/args_test.c

## Purpose
Tests the refactored `nbd-client` argument parser exposed through `parse_nbd_client_args()` and `CLIENT` initialization/free helpers.

## Main Entry Points
- Test helpers `TEST_ASSERT` and `TEST_ASSERT_STR_EQ` count and report pass/fail status.
- Individual test functions cover device-only arguments, normal connection syntax, options, connection checking, disconnect, export listing, version display, netlink-specific options, and error cases.
- `main()` runs all tests and returns success only if every assertion passed.

## Test Coverage
The tests verify that `nbd0` and `/dev/nbd0` are treated as device/nbdtab-style inputs, normal host/port/device parsing works, `-N`, `-b`, and `-timeout` populate fields, `-c` and `-d` set action flags, `-l` lists exports without a device, `-V` marks version output, and invalid block sizes or bad argument counts request process exit. Conditional checks assert different behavior for `-i` and `-L` depending on `HAVE_NETLINK`.

## Dependencies
Includes `../../args.h` and links against `../../args.c`.

## Risks and Notes
The test suite is print-and-count based rather than using a unit-test framework. It assumes parser behavior where some single-argument device forms populate both `hostn` and `dev`.
