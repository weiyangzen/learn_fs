<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/openat2-resolvetab.h -->
# sources/security-integrity/audit-userspace/auparse/openat2-resolvetab.h

## Purpose
Maps `openat2` resolve constraint bits to names.

## Important APIs, types, and functions
The `_S` table covers `RESOLVE_NO_XDEV`, `NO_MAGICLINKS`, `NO_SYMLINKS`, `BENEATH`, `IN_ROOT`, and `CACHED`.

## Control flow
Generated table data is scanned by `interpret.c:print_openat2_resolve` for `AUPARSE_TYPE_RESOLVE`.

## State and persistence behavior
Static table data only.

## Dependencies and integration points
Tracks `include/uapi/linux/openat2.h`. Integrated with audit record type handling for `AUDIT_OPENAT2`.

## Risks and test signals
Risks are missing new resolve flags and buffer sizing if table grows. Tests should verify single and combined flags plus zero/unknown fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/openat2-resolvetab.h -->
