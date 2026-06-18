# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/test_cases/heimdal2.h

## Purpose
`heimdal2.h` is the expected generated header for the negative-base `kadm` fixture.

## Important APIs, Types, and Functions
It defines `KADM_*` constants, declares the generated table and initializer functions, sets `ERROR_TABLE_BASE_kadm`, and provides old compatibility aliases.

## Control Flow
There is no runtime flow. The header validates that macro values progress correctly through negative ranges and explicit index jumps.

## State, Persistence, Dependencies, Risks, and Test Signals
State is external in `heimdal2.c`. Dependencies are `<et/com_err.h>` and AWK base arithmetic. Risks include sign/carry drift between header and C generation. Test signal is exact `compile_et` diff and usable constants for negative error codes.
