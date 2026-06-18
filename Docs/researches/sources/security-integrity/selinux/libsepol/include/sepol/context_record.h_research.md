# sources/security-integrity/selinux/libsepol/include/sepol/context_record.h

Purpose: Declares the opaque public record API for SELinux security contexts.

Important APIs and types: Defines `sepol_context_t` and exports user/role/type/MLS getters and setters, create/clone/free, `sepol_context_from_string`, and `sepol_context_to_string`.

Control flow: Callers build contexts field-by-field or parse colon-separated strings; policy-aware validation is delegated to `context.h`.

State and persistence: The implementation stores heap-duplicated strings for user, role, type, and optional MLS. Records by themselves are not persisted in policydb collections.

Dependencies and integration points: Depends on `sepol_handle_t`; used by node/port/interface/user APIs and internal context conversion.

Risks: Setters expect non-null strings. String parsing accepts three or four components but does not validate policy existence; callers need `sepol_context_check`.

Test signals: Parse/to-string round trips, clone/free, optional MLS handling, and malformed strings validate this surface.
