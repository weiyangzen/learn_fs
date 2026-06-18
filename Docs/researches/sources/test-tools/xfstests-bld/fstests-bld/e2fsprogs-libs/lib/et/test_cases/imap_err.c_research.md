# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/test_cases/imap_err.c

## Purpose
`imap_err.c` is an expected generated C file for an IMAP error table with a negative encoded base.

## Important APIs, Types, and Functions
It defines an IMAP message array, `et_imap_error_table` with base `-1904809472L` and 30 messages, and generated initializer functions.

## Control Flow
The initializer path follows the generated idempotent registration pattern. Messages are indexed contiguously from the table base.

## State, Persistence, Dependencies, Risks, and Test Signals
State is list registration. Dependencies include negative base arithmetic in AWK and com_err structures. Risks include signed-code portability and string drift versus the source `.et`. Test signals are regeneration diffs and successful lookup of IMAP constants.
