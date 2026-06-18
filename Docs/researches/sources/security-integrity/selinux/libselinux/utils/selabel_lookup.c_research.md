<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/selabel_lookup.c -->
# sources/security-integrity/selinux/libselinux/utils/selabel_lookup.c

## Purpose
Generic CLI for looking up a label by backend, key, optional type, spec file, validation, and raw/translated mode.

## Important APIs, Types, And Functions
Maps backend names to `SELABEL_CTX_*`, opens `selabel_handle`, calls `selabel_lookup()` or `selabel_lookup_raw()`, and prints the default context.

## Control Flow
Options are parsed with `getopt`; lookup errors distinguish no match, invalid key/type/validation, and other errno cases.

## State And Persistence Behavior
Read-only label spec access.

## Dependencies And Integration Points
Useful for file, media, X, DB, Android property, and Android service label backend diagnostics.

## Risks And Test Signals
Test all backends, missing key, type parsing, raw mode, no-match, validation failure, and custom spec files.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/selabel_lookup.c -->
