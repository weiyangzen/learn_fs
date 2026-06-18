# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/test_cases/imap_err.h

## Purpose
`imap_err.h` is the expected generated header for the IMAP negative-base fixture.

## Important APIs, Types, and Functions
It defines `IMAP_*` error constants, declares `et_imap_error_table`, initializer functions, `ERROR_TABLE_BASE_imap`, and old compatibility aliases.

## Control Flow
There is no runtime control flow. It provides compile-time constants for callers and for diff-based generator testing.

## State, Persistence, Dependencies, Risks, and Test Signals
State is external in `imap_err.c`. Dependencies are `<et/com_err.h>`. Risks are macro value drift if signed base logic changes. Test signals are exact generated header diff and usable IMAP constants.
