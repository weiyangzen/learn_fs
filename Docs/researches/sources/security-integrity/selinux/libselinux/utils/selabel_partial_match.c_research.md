<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/selabel_partial_match.c -->
# sources/security-integrity/selinux/libselinux/utils/selabel_partial_match.c

## Purpose
CLI for checking whether a path has any possible full or partial file-context match.

## Important APIs, Types, And Functions
Opens a file-label handle and calls `selabel_partial_match(hnd, path)`.

## Control Flow
Requires `-p path`; optional `-f` and `-v` configure the handle. It prints `TRUE` or `FALSE` and returns the boolean value.

## State And Persistence Behavior
Read-only.

## Dependencies And Integration Points
Matches restorecon sysfs pruning and partial-digest behavior.

## Risks And Test Signals
Test partial versus no partial paths, validation/spec-file options, missing path, and return-code expectations where `TRUE` returns nonzero.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/selabel_partial_match.c -->
