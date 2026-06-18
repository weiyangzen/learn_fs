# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/test_cases/heimdal3.h

## Purpose
`heimdal3.h` is the expected generated header for the small `h3test` fixture.

## Important APIs, Types, and Functions
It defines `H3TEST_TEST1`, `H3TEST_TEST2`, declares `et_h3test_error_table` and initializers, and defines table-base compatibility macros.

## Control Flow
There is no runtime control flow.

## State, Persistence, Dependencies, Risks, and Test Signals
State is provided by `heimdal3.c`. Dependencies are `<et/com_err.h>`. Risks are mismatch with C output if base-name generation changes. Test signal is exact header diff in `make check`.
