<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/selabel_get_digests_all_partial_matches.c -->
# sources/security-integrity/selinux/libselinux/utils/selabel_get_digests_all_partial_matches.c

## Purpose
Reports calculated and stored digest values for all file-context specs that partially match directories under a path.

## Important APIs, Types, And Functions
Uses `selabel_get_digests_all_partial_matches()` for each directory found by `fts`, with options for spec file, validation, and recursive traversal.

## Control Flow
The utility opens a file-label handle, traverses the starting path physically, handles directories, prints whether xattr and calculated digests match, and formats digest bytes as hex.

## State And Persistence Behavior
Read-only: it does not set or remove digest xattrs.

## Dependencies And Integration Points
Closely mirrors restorecon digest decision logic and depends on FTS and label digest APIs.

## Risks And Test Signals
Test recursive and single-directory modes, no digest for `<<none>>`, missing xattr, mismatched xattr, allocation failures, FTS errors, and validation/spec-file options.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/selabel_get_digests_all_partial_matches.c -->
