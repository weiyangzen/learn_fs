# sources/security-integrity/selinux/libselinux/include/selinux/get_default_type.h

## Purpose
`get_default_type.h` declares functions for locating and reading the default SELinux type/domain associated with a role.

## Important APIs, types, and functions
`selinux_default_type_path()` returns the path to the default type file. `get_default_type(const char *role, char **type)` finds the default type for a role and returns caller-owned storage that must be freed with `free()`.

## Control flow
Callers typically locate the config path only for diagnostics or custom reading. Normal use passes a role to `get_default_type()`, checks for `0` success or `-1` failure, uses the returned type string, and frees it.

## State and persistence behavior
The API reads SELinux configuration data and allocates memory for results. It does not modify policy or persist state.

## Dependencies and integration points
It is part of libselinux's login/session support and complements role/context selection APIs in `get_context_list.h` and path discovery APIs in `selinux.h`.

## Risks and edge cases
Callers must handle absent role mappings, unreadable configuration, NULL output pointers, and memory ownership. The header documents `free()` rather than `freecon()`, so using the wrong deallocator is a caller bug.

## Test signals
Tests should cover existing and missing roles, unreadable default type files, malformed records, memory allocation failures, returned path stability, and correct caller freeing.
