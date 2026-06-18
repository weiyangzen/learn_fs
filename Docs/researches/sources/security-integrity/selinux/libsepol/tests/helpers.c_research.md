# sources/security-integrity/selinux/libsepol/tests/helpers.c

## Purpose
`helpers.c` implements common CUnit helper routines for loading source policies and finding declarations by symbol.

## Important APIs and Control Flow
`test_load_policy()` initializes a policydb, sets policy type, MLS flag, and max module policy version, chooses the generated `.std` or `.mls` fixture path, and calls `read_source_policy()`. `test_find_decl_by_sym()` looks up a scope entry, requires `SCOPE_DECL` with exactly one declaration ID, and returns the corresponding `avrule_decl_t`.

## Dependencies, Risks, and Tests
It depends on checkpolicy parser utilities, policy expansion/declaration types, and CUnit. Path construction checks negative `snprintf()` but not truncation. Declaration lookup returns `NULL` for absent, required-only, or ambiguous scopes. Suites that load generated policies exercise this helper.
