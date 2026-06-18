<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/getconlist.c -->
# sources/security-integrity/selinux/libselinux/utils/getconlist.c

## Purpose
Prints the ordered list of login contexts available to a user from a current or supplied context.

## Important APIs, Types, And Functions
Parses `-l level`, validates SELinux enabled, obtains current context with `getcon()` when needed, validates supplied context, and calls `get_ordered_context_list()` or `_with_level()`.

## Control Flow
Requires `user [context]`; prints each returned context on success and frees arrays.

## State And Persistence Behavior
Read-only; allocates context list and optional level/current context.

## Dependencies And Integration Points
Uses get-context-list policy logic and SELinux enabled checks.

## Risks And Test Signals
Test disabled SELinux, invalid contexts, explicit versus current context, level override, no contexts, and allocation failure paths.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/getconlist.c -->
