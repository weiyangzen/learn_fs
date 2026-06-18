# sources/security-integrity/selinux/libselinux/src/get_context_list.c

Purpose: Builds ordered login/default context lists for a user from per-user and global SELinux context configuration, with optional role and MLS level filtering.

Important APIs/types/functions: public APIs include `get_ordered_context_list()`, `get_ordered_context_list_with_level()`, `get_default_context()`, `get_default_context_with_level()`, `get_default_context_with_role()`, and `get_default_context_with_rolelevel()`. Helpers parse context config with `get_context_user()` and fall back through `get_failsafe_context()`.

Control flow: if no source context is supplied, current context is read with `getcon()`. The source context is parsed to role/type/range. Per-user config is tried first, then global default contexts. Each matching line maps partial contexts to full `user:partial` contexts, applies the source MLS range, removes duplicates, and validates candidates through `security_check_context()`. If no reachable contexts are found, the failsafe context file is prefixed with the user.

State and persistence: allocates caller-owned NULL-terminated arrays; reads policy configuration files but does not modify them.

Dependencies and integration: uses context parsing, path helpers, validation callbacks, `freeconary()`, and login/session consumers.

Risks and test signals: parsing accepts partial contexts and has many fallback paths. Tests should cover per-user precedence, global fallback, duplicate suppression, invalid candidate skip, explicit level override, role filtering, failsafe recovery, and malformed files.
