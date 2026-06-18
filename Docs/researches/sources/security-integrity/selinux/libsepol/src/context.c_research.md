# sources/security-integrity/selinux/libsepol/src/context.c

Purpose: Implements internal/public context validation and conversion between records, strings, and numeric `context_struct_t`.

Important APIs and functions: `policydb_context_isvalid`, deprecated `sepol_check_context`, `context_is_valid`, `context_to_string`, `context_from_record`, `context_to_record`, `context_from_string`, and `sepol_context_check`.

Control flow: Validation checks one-based user/role/type bounds, role-to-type cache, user-to-role cache, and MLS validity. Record-to-struct conversion resolves names through policydb symbol tables, rejects type attributes, enforces MLS presence/absence, parses MLS strings, and validates. Struct-to-record/string conversions use value-to-name indexes and MLS formatting helpers.

State and persistence: Allocates temporary contexts/strings/records; does not mutate policydb. Deprecated check uses service SID conversion.

Dependencies and integration points: Uses policydb services, public context records, internal MLS helpers, debug/handle/private utilities.

Risks: Symbol indexes must be populated. MLS mismatch is a hard error. Caller owns returned allocations.

Test signals: Valid/invalid contexts, object_r shortcut behavior, MLS enabled/disabled, type attribute rejection, string length overflow, and service compatibility tests.
