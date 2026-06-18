# sources/user-network-fs/samba/source3/lib/audit.c

Purpose: maps LSA audit categories between numeric constants, symbolic strings, smb.conf parameter tokens, descriptions, and policy result strings.

Important APIs/types/functions: static `audit_category_tab`; public `audit_category_str()`, `audit_param_str()`, `audit_description_str()`, `get_audit_category_from_param()`, and `audit_policy_str()`.

Control flow: lookup functions linearly scan the sentinel-terminated table and return null on unknown category. `get_audit_category_from_param()` uses case-insensitive token comparisons and writes `Undefined` before selecting a category. `audit_policy_str()` formats `None`, `Success`, `Failure`, or `Success, Failure` using talloc.

State and persistence: stateless except for constant table data and caller-owned talloc allocations for policy strings.

Dependencies/integration: consumes generated LSA constants from `../librpc/gen_ndr/lsa.h`, Samba string helpers, DEBUG logging, and talloc.

Risks/test signals: category spelling follows upstream constants including `PROCCESS`; unknown parameters log at level 0 and return false. Tests should cover every table row round-trip, unknown categories returning null, unknown params preserving `Undefined`, and combined success/failure policy formatting.
