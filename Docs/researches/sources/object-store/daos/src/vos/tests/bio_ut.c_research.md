# sources/object-store/daos/src/vos/tests/bio_ut.c

## Purpose
Standalone entry point for BIO/WAL unit tests. It initializes DAOS debug and a self-contained VOS instance, then runs WAL tests.

## Important APIs, types, and functions
- Global `ut_args` holds BIO unit-test context and seed.
- `ut_init()` calls `daos_debug_init`, `vos_self_init`, and stores `vos_xsctxt_get()`.
- `ut_fini()` calls `vos_self_fini` and `daos_debug_fini`.
- `main()` parses `--db_path`, `--seed`, and `--help`, then calls `run_wal_tests()`.

## Control flow
The program registers cmocka-style alternative assertions, chooses a random seed from time unless supplied, defaults `db_path` to `/mnt/daos`, prints the seed, and runs all WAL tests. `ut_init`/`ut_fini` are exported for test suites rather than called directly by `main`.

## State and persistence behavior
State includes the configured DB/storage path, random seed, and VOS xstream context. Persistent effects are whatever WAL tests create under the selected path through VOS/BIO.

## Dependencies and integration points
Depends on `bio_ut.h`, VOS TLS, DAOS debug, `vos_self_init`, and the WAL test implementation (`run_wal_tests`). It is a narrower binary than the full `vos_tests` launcher.

## Risks and edge cases
`db_path` is a fixed 100-byte buffer; long input is truncated. The main path does not call `ut_init` itself, so WAL tests must manage fixture initialization through exported helpers. Defaulting to `/mnt/daos` requires an appropriate test environment.

## Test signals
Signals are successful option parsing, printed seed reproducibility, successful VOS initialization in WAL fixtures, and `run_wal_tests()` return code.
