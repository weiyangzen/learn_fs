# sources/security-integrity/selinux/libsepol/include/sepol/context.h

Purpose: Declares public validation helpers for SELinux contexts and MLS strings.

Important APIs and functions: Deprecated `sepol_check_context`, plus `sepol_context_check`, `sepol_mls_contains`, and `sepol_mls_check`.

Control flow: Callers create or parse `sepol_context_t` records, then validate them against a loaded `sepol_policydb_t`; MLS helpers compare/check string forms against policy MLS definitions.

State and persistence: Functions do not persist state except for deprecated compatibility paths that operate through service-layer global policy/SID state.

Dependencies and integration points: Depends on `context_record.h`, `policydb.h`, and `handle.h`; implementation bridges public records to internal `context_struct_t`.

Risks: Deprecated `sepol_check_context` depends on global service state and is harder to reason about. MLS presence must match whether the policydb is MLS-enabled.

Test signals: Valid/invalid user:role:type[:mls] records, MLS disabled/enabled cases, and deprecated compatibility calls provide coverage.
