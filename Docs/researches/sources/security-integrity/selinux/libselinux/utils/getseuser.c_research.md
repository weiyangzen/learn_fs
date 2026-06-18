<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/getseuser.c -->
# sources/security-integrity/selinux/libselinux/utils/getseuser.c

## Purpose
Diagnostic utility for resolving a Linux user to SELinux user/level and listing ordered contexts from a supplied context.

## Important APIs, Types, And Functions
Calls `getseuserbyname()`, validates `fromcon`, then calls `get_ordered_context_list_with_level()`.

## Control Flow
Requires `linuxuser fromcon`, checks SELinux enabled, prints mapping, then prints numbered contexts or no-match message.

## State And Persistence Behavior
Read-only login mapping and policy access.

## Dependencies And Integration Points
Connects `seusers.c` and default context list logic.

## Risks And Test Signals
Test disabled SELinux, unknown users, invalid from context, no valid contexts, MLS levels, and returned list cleanup.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/getseuser.c -->
