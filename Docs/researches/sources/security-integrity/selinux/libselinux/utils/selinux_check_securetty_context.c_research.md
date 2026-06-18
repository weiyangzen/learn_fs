<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/selinux_check_securetty_context.c -->
# sources/security-integrity/selinux/libselinux/utils/selinux_check_securetty_context.c

## Purpose
CLI wrapper around secure TTY context type checking.

## Important APIs, Types, And Functions
Loops over supplied contexts and calls `selinux_check_securetty_context()` for each.

## Control Flow
Every input prints either `securetty` or `not securetty`; the program returns success even for non-secure contexts.

## State And Persistence Behavior
Read-only policy config access.

## Dependencies And Integration Points
Thin diagnostic for `src/selinux_check_securetty_context.c`.

## Risks And Test Signals
Test multiple contexts, invalid contexts, missing securetty file, and caller expectations around always-success exit status.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/selinux_check_securetty_context.c -->
