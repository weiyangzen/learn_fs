# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/test_cases/heimdal.c

## Purpose
`heimdal.c` is an expected generated C file for a Kerberos-style table with Heimdal-compatible gaps and reserved messages.

## Important APIs, Types, and Functions
It defines a large `text[]` array, `et_krb_error_table` with base `39525376L` and 82 messages, and both global and list-local initializer functions.

## Control Flow
The initializer path matches the generated pattern: avoid duplicate message arrays, allocate a list node or use the static fallback, and append it to the supplied list.

## State, Persistence, Dependencies, Risks, and Test Signals
State is error-table registration in `_et_list` or a caller list. Dependencies include generated com_err structures and Kerberos-style error numbering. Risks include reserved-index drift and duplicate table-name collision with other `krb` fixtures. Test signal is exact regeneration by `compile_et`.
