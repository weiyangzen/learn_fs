# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/test_cases/continuation.h

## Purpose
`continuation.h` is the expected generated header for the continuation error-table fixture.

## Important APIs, Types, and Functions
It defines `CHPASS_UTIL_PASSWORD_IN_DICTIONARY`, declares `et_ovk_error_table`, `initialize_ovk_error_table()`, `initialize_ovk_error_table_r()`, `ERROR_TABLE_BASE_ovk`, and old compatibility aliases.

## Control Flow
There is no runtime control flow; consumers include it to use the generated numeric constant and initializer.

## State, Persistence, Dependencies, Risks, and Test Signals
State is external and provided by `continuation.c`. Dependencies are `<et/com_err.h>`. Risks are mismatch with generated C if table base or prefix handling changes. Test signal is exact header diff after running `compile_et`.
