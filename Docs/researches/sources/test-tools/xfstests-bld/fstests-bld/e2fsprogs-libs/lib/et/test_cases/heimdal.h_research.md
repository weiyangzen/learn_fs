# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/test_cases/heimdal.h

## Purpose
`heimdal.h` is the expected generated header for the Heimdal Kerberos fixture.

## Important APIs, Types, and Functions
It defines many `KRBET_*` error constants, declares `et_krb_error_table`, initializer functions, `ERROR_TABLE_BASE_krb`, and compatibility aliases.

## Control Flow
There is no runtime control flow. The header is consumed by code that wants named constants and explicit table initialization.

## State, Persistence, Dependencies, Risks, and Test Signals
State is in `heimdal.c`. Dependencies are `<et/com_err.h>` and matching generated table base. Risks include constant collisions with `simple.h`, which intentionally uses the same `krb` table base with a different fixture. Test signal is exact header regeneration.
