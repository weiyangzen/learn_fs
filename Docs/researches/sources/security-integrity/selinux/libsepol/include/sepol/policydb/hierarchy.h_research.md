# sources/security-integrity/selinux/libsepol/include/sepol/policydb/hierarchy.h

Purpose: Declares internal hierarchy/bounds validation helpers for users, roles, and types.

Important APIs and functions: `hierarchy_add_bounds`, `bounds_destroy_bad`, `bounds_check_type`, `bounds_check_users`, `bounds_check_roles`, `bounds_check_types`, and `hierarchy_check_constraints`.

Control flow: Expansion/validation code adds or checks bounds relationships and scans avtab entries for child permissions exceeding parent permissions.

State and persistence: Bounds fields live in user/role/type datums; bad avtab lists are temporary diagnostic state.

Dependencies and integration points: Depends on avtab and policydb internals; used by module expansion, validation, and fuzz harnesses.

Risks: Bounds enforcement is security-sensitive because it restricts child domains/users/roles. Diagnostics must free bad-entry lists.

Test signals: Policies with valid and violating typebounds/rolebounds/userbounds and hierarchy constraint checks validate the API.
