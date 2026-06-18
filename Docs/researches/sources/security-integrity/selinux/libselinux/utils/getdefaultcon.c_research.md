<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/getdefaultcon.c -->
# sources/security-integrity/selinux/libselinux/utils/getdefaultcon.c

## Purpose
Prints the default login context for a Linux user, with optional role, level, service, and verbose output.

## Important APIs, Types, And Functions
Uses `getseuser()`, `get_default_context_with_level()`, and `get_default_context_with_rolelevel()`. Options are `-r`, `-l`, `-s`, and `-v`.

## Control Flow
After resolving current/from context and SELinux user/default level, it computes a default context and prints either the context alone or a verbose transition description.

## State And Persistence Behavior
Read-only policy and login mapping access.

## Dependencies And Integration Points
Connects `seusers.c` login mapping to default-context selection APIs.

## Risks And Test Signals
Test service-specific mappings, role/level overrides, invalid from contexts, disabled SELinux, verbose output, and memory cleanup when `level` aliases `dlevel`.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/getdefaultcon.c -->
