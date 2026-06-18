<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/selabel_compare.c -->
# sources/security-integrity/selinux/libselinux/utils/selabel_compare.c

## Purpose
Compares two SELinux label specification files using a selected backend.

## Important APIs, Types, And Functions
Parses backend and validation options, opens two `selabel_handle`s with `SELABEL_OPT_PATH` and `SELABEL_OPT_VALIDATE`, and calls the backend `selabel_cmp()` operation.

## Control Flow
Backend names map to `SELABEL_CTX_*` constants, defaulting to file. Compare results are printed as equal, subset/superset, incomparable, or error depending on libselinux enum results.

## State And Persistence Behavior
Read-only label spec access.

## Dependencies And Integration Points
Exercises backend comparison callbacks, validation, and label handle lifecycle.

## Risks And Test Signals
Test each backend name, validation on/off, open failures, equal files, subset/superset/incomparable specs, and unknown backend handling.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/selabel_compare.c -->
