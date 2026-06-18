# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/test_cases/heimdal2.c

## Purpose
`heimdal2.c` is an expected generated C file for a negative-base `kadm` Kerberos administration error table.

## Important APIs, Types, and Functions
It defines `text[]`, `et_kadm_error_table` with base `-1783126272L` and 68 messages, static `link`, and `initialize_kadm_error_table()` variants.

## Control Flow
Initialization follows the generated idempotent list-append pattern. The table includes explicit reserved messages created from indexed gaps in the source `.et`.

## State, Persistence, Dependencies, Risks, and Test Signals
State is registration in `_et_list` or a caller list. Dependencies include correct negative table-base arithmetic in `et_c.awk` and `et_h.awk`. Risks center on signed AWK/base encoding portability. Test signals are exact generated output and successful lookup of negative-base codes.
