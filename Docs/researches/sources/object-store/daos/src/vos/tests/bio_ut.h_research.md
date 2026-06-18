# sources/object-store/daos/src/vos/tests/bio_ut.h

## Purpose
Shared header for BIO/WAL unit tests. It defines common includes, fault-injection skip behavior, and the test argument structure exported by `bio_ut.c`.

## Important APIs, types, and functions
- `FAULT_INJECTION_REQUIRED()` either no-ops when built with fault injection or prints a skip message and calls `skip()`.
- `struct bio_ut_args` carries xstream BIO context, metadata context, pool UUID, and random seed.
- Exports `ut_args`, `ut_init`, `ut_fini`, and `run_wal_tests`.

## Control flow
The header provides macros and declarations only. Test files include it to access common initialization and conditional skipping.

## State and persistence behavior
It declares shared state but does not own persistence. The struct fields represent runtime BIO/VOS contexts and seed values.

## Dependencies and integration points
Includes cmocka, DAOS common/test libraries, sys_db, and server BIO headers. It is the glue between the BIO test launcher and WAL test implementation.

## Risks and edge cases
Tests requiring fault injection must use the macro or they may produce false failures in builds without fault injection. Consumers must ensure `ut_init`/`ut_fini` are paired and must not assume all struct fields are initialized by every test.

## Test signals
Signals are build-time availability of declarations, correct skip behavior without fault injection, and shared seed/context propagation into WAL tests.
