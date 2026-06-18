<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/selabel_lookup_best_match.c -->
# sources/security-integrity/selinux/libselinux/utils/selabel_lookup_best_match.c

## Purpose
CLI for finding the best file-context match for a path with optional alias/link paths.

## Important APIs, Types, And Functions
Parses `-p path`, optional `-m mode`, `-f file`, `-v`, and `-r`, builds a NULL-terminated aliases array, and calls `selabel_lookup_best_match()` or raw variant.

## Control Flow
Best-match precedence is handled by libselinux: exact real path, exact alias, then longest fixed prefix. The utility reports specific errors for no match and invalid inputs.

## State And Persistence Behavior
Read-only label lookup; dynamically allocates alias copies.

## Dependencies And Integration Points
Exercises file-label best-match logic used by alias-aware callers.

## Risks And Test Signals
Test zero/multiple aliases, forced modes, raw output, custom spec files, missing path operand, unknown mode letters, and allocation cleanup on partial alias duplication failure.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/selabel_lookup_best_match.c -->
