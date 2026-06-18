# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/test_cases/simple.h

## Purpose
`simple.h` is the expected generated header for the small `krb` fixture.

## Important APIs, Types, and Functions
It defines `KRB_*` constants, declares `et_krb_error_table` and initializer functions, and provides `ERROR_TABLE_BASE_krb`, `init_krb_err_tbl`, and `krb_err_base`.

## Control Flow
There is no runtime control flow.

## State, Persistence, Dependencies, Risks, and Test Signals
State is in `simple.c`. Dependencies are `<et/com_err.h>`. Risks are collision or confusion with the larger `heimdal.h` fixture because both use `krb`. Test signal is exact header regeneration.
