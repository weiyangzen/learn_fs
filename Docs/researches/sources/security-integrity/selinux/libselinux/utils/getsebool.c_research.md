<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/getsebool.c -->
# sources/security-integrity/selinux/libselinux/utils/getsebool.c

## Purpose
Prints active and pending SELinux boolean values.

## Important APIs, Types, And Functions
Supports `-a` for all booleans or explicit names. Uses `security_get_boolean_names()`, `security_get_boolean_active()`, `security_get_boolean_pending()`, and `selinux_boolean_sub()`.

## Control Flow
Checks SELinux enabled, builds the boolean name list, prints `name --> on/off` plus pending state when it differs, and frees names.

## State And Persistence Behavior
Read-only boolean access.

## Dependencies And Integration Points
Thin diagnostic for boolean APIs and boolean alias/substitution handling.

## Risks And Test Signals
Test disabled SELinux, `-a` with no booleans, explicit names, pending different from active, EACCES skip for all-booleans mode, unknown names, and alias allocation failures.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/getsebool.c -->
