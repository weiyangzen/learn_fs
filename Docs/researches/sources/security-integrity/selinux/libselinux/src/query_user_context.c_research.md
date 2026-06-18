<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/query_user_context.c -->
# sources/security-integrity/selinux/libselinux/src/query_user_context.c

## Purpose
Provides terminal-interactive helpers for selecting or manually entering a login context.

## Important APIs, Types, And Functions
`query_user_context()` prints a default context and optionally presents a numbered menu. `manual_user_enter_context()` constructs a context using `context_new()`, `context_user_set()`, `context_role_set()`, `context_type_set()`, optional `context_range_set()`, and validates it with `security_check_context()`.

## Control Flow
The default list entry is selected unless the user answers yes to choosing another one. Manual entry loops until the user provides all required fields and the resulting context validates, or declines entry.

## State And Persistence Behavior
No SELinux state is changed. The selected context is heap-duplicated for the caller.

## Dependencies And Integration Points
Uses stdin/stdout, libselinux context manipulation, `is_selinux_mls_enabled()`, and security context validation.

## Risks And Test Signals
Risks are interactive blocking, fixed field buffers, unchecked `strtol()` menu parsing, and use of `fflush(stdin)`. Tests should use scripted stdin for menu selection, EOF, MLS enabled/disabled, invalid contexts, and allocation failures where practical.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/query_user_context.c -->
