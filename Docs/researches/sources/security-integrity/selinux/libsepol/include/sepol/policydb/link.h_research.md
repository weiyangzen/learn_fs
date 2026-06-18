# sources/security-integrity/selinux/libsepol/include/sepol/policydb/link.h

Purpose: Declares the internal module linker entry point.

Important APIs and functions: `link_modules(sepol_handle_t *handle, policydb_t *b, policydb_t **mods, int len, int verbose)`.

Control flow: Linker combines a base policydb with module policydbs, resolving scopes, required symbols, declarations, and rules before expansion.

State and persistence: Mutates the base policydb to include linked module declarations and rule structures.

Dependencies and integration points: Wrapped by public `sepol_link_modules` and used in fuzzing. Depends on handles, errcodes, and internal policydb.

Risks: Link order, duplicate declarations, optional blocks, and unresolved requirements are high-risk correctness points.

Test signals: Multiple-module link scenarios, missing requirements, duplicate symbols, optional blocks, and verbose diagnostics validate this boundary.
