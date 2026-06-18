# sources/security-integrity/selinux/libselinux/include/selinux/get_context_list.h

## Purpose
`get_context_list.h` declares APIs for determining authorized and preferred SELinux login/session contexts for a Linux user, optionally constrained by role or MLS level.

## Important APIs, types, and functions
The default SELinux user fallback is `SELINUX_DEFAULTUSER`. APIs include `get_ordered_context_list()`, `get_ordered_context_list_with_level()`, `get_default_context()`, `get_default_context_with_level()`, `get_default_context_with_role()`, `get_default_context_with_rolelevel()`, `query_user_context()`, and `manual_user_enter_context()`.

## Control flow
Callers supply a target user and optional source context, level, or role. The library computes policy-authorized contexts, orders them according to customizable preferences, returns a list or default context, or asks the user to select/enter a context. `fromcon == NULL` means the current context is used.

## State and persistence behavior
Returned context arrays are caller-owned and freed with `freeconary()`. Returned single contexts are caller-owned and freed with `freecon()`. The functions consult policy and preference data but do not persist changes themselves.

## Dependencies and integration points
The header includes `selinux/selinux.h` for memory-freeing and context APIs. It integrates with login managers, PAM/session setup, role selection, MLS/MCS level handling, and user preference files.

## Risks and edge cases
The include guard name `_SELINUX_GET_SID_LIST_H_` does not match the file name, which is harmless but confusing. Interactive functions are unsuitable for noninteractive services unless carefully gated. Callers must free using the libselinux-specific free helpers rather than plain `free()` for contexts.

## Test signals
Tests should cover reachable and unreachable users, role-restricted lookup, MLS level override, NULL `fromcon`, ordered preference behavior, no-policy/error paths, interactive selection cancellation, and ownership/freeing contracts.
