<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/normalize-internal.h -->
# sources/security-integrity/audit-userspace/auparse/normalize-internal.h

## Purpose
Defines internal numeric constants used by auparse event normalization for account classes, syscall object/action classes, object kinds, and event kinds.

## Important APIs, types, and functions
Constants include account thresholds (`NORM_ACCT_*`), syscall/object action classes (`NORM_FILE`, `NORM_EXEC`, `NORM_SOCKET_*`, `NORM_SECURITY_*`, etc.), object kind ids (`NORM_WHAT_*`), and event kind ids (`NORM_EVTYPE_*`).

## Control flow
No execution occurs here. `normalize.c` assigns these constants while analyzing events, and generated map helpers convert them to strings.

## State and persistence behavior
Static compile-time constants only.

## Dependencies and integration points
Used by `normalize.c`, `normalize_*_map.h`, and the generated table layer. Values must stay stable relative to map entries.

## Risks and test signals
Risks are adding constants without map entries, reusing ids, or changing numeric values without regenerating tables. Tests should verify every emitted object/event kind has a string mapping.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/normalize-internal.h -->
