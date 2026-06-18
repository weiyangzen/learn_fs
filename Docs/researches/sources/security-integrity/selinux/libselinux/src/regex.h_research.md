<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/regex.h -->
# sources/security-integrity/selinux/libselinux/src/regex.h

## Purpose
Defines the internal regular-expression backend contract used by libselinux file labeling and context compilation.

## Important APIs, Types, And Functions
Declares match result constants, opaque `struct regex_data`, backend-specific `struct regex_error_data`, and functions for architecture/version reporting, compile/load/write/free/match/compare/error-format operations.

## Control Flow
The header documents expected success and failure returns for compile, mmap load, serialization, and match operations.

## State And Persistence Behavior
No state lives in the header, but it describes serialized regex persistence and ownership expectations for returned `regex_data`.

## Dependencies And Integration Points
Includes PCRE2 or PCRE headers depending on `USE_PCRE2`, plus stdio and bool; forward-declares `struct mmap_area`.

## Risks And Test Signals
Risks are public-internal API mismatch with `regex.c` and backend-specific struct assumptions. Compile tests for both regex backends and file-context binary round trips are the main signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/regex.h -->
