# sources/security-integrity/selinux/libselinux/src/context.c

Purpose: Provides the public `context_t` object implementation for parsing, inspecting, modifying, and rendering SELinux context strings.

Important APIs/types/functions: `context_new()`, `context_free()`, `context_str()`, `context_to_str()`, getters `context_user_get`, `context_role_get`, `context_type_get`, `context_range_get`, and setters for each component. Internal `context_private_t` stores a cached rendered string plus four components.

Control flow: `context_new()` validates separators and whitespace, requires three or four logical components while allowing MLS range to contain additional colons, duplicates components, and returns a wrapper. `context_str()` frees and rebuilds the cached string from current components. `context_to_str()` returns a fresh string. Setters reject tabs/newlines/carriage returns and reject colon or space except in range.

State and persistence: each context owns heap strings and a cached rendered form. Setters invalidate only the affected component; render functions recreate strings.

Dependencies and integration: included through `context_internal.h` and public `selinux/context.h`; used by login-context selection and customizable type checks.

Risks and test signals: `context_str()` returns an internal pointer invalidated by later mutations. Tests should cover MLS ranges with colons/spaces, invalid whitespace, missing components, setter validation, allocation failure cleanup, and repeated render calls.
