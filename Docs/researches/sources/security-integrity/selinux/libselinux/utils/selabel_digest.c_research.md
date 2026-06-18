<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/selabel_digest.c -->
# sources/security-integrity/selinux/libselinux/utils/selabel_digest.c

## Purpose
Utility for retrieving and optionally checking the digest associated with a selabel handle.

## Important APIs, Types, And Functions
Uses `selabel_open()` with digest options, `selabel_digest()` to obtain digest bytes and specfile list, and `run_check_digest()` to compare against external command output when requested.

## Control Flow
Command-line options select spec file, validation, and digest checking behavior. The digest is printed in hex along with contributing files, or compared to a supplied command/check result.

## State And Persistence Behavior
Read-only; digest bytes and file list are allocated and freed locally.

## Dependencies And Integration Points
Exercises `SELABEL_OPT_DIGEST` and file-label digest generation used by restorecon.

## Risks And Test Signals
Test missing spec file, digest disabled/unavailable, multiple specfiles, command-check mismatch, validation failures, and hex formatting.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/selabel_digest.c -->
