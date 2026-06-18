<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/selinuxexeccon.c -->
# sources/security-integrity/selinux/libselinux/utils/selinuxexeccon.c

## Purpose
Prints the process context that would result from executing a command from a supplied or current context.

## Important APIs, Types, And Functions
`get_selinux_proc_context()` gets the file context and calls `security_compute_create()` for class `process`. `main()` obtains/validates the source context.

## Control Flow
Requires `command [fromcon]`, computes transition, prints it on success, and reports perror on failure.

## State And Persistence Behavior
Read-only; it does not set exec context or execute the command.

## Dependencies And Integration Points
Diagnostic companion to `setexecfilecon()`.

## Risks And Test Signals
Test current versus supplied context, invalid supplied context, missing command file, no transition, and process class lookup failure.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/selinuxexeccon.c -->
