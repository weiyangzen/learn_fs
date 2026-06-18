# sources/user-network-fs/samba/source4/torture/local/local.c

## Purpose
`local.c` is the registration hub for Samba-specific local smbtorture suites.

## Important APIs, types, and functions
The `suite_generators` array lists local suite factory functions for binding strings, crypto, messaging, utility libraries, NDR/TDR, registry, NSS, FSRVP, mdspkt, and many others. `torture_local_init()` creates the top-level `local` suite, adds direct `talloc`, `replace`, and `crypto.md4` tests, then adds every generated sub-suite.

## Control flow
Smbtorture calls `torture_local_init()` during module initialization. The function iterates until the NULL sentinel in `suite_generators`, attaches each child suite, sets a description, and registers the top-level suite.

## State and persistence behavior
This file only builds suite metadata in memory. Runtime state and persistence belong to the child tests.

## Dependencies and integration points
It integrates many local test subsystems through generated proto headers and module init registration. It is the single entry point for the `TORTURE_LOCAL` module built by `local/wscript_build`.

## Risks and edge cases
Adding a generator without linking its implementation breaks the module. The order matters where child suites have implicit dependencies, such as dbspeed's TDB result before LDB ratio inside that child suite.

## Test signals
Successful initialization means all listed local test suites are reachable under `smbtorture local`, providing broad local coverage.
