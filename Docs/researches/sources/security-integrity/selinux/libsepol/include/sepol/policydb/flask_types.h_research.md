# sources/security-integrity/selinux/libsepol/include/sepol/policydb/flask_types.h

Purpose: Defines core Flask/SELinux scalar types and constants.

Important APIs and types: `sepol_security_context_t`, `sepol_access_vector_t`, `sepol_security_class_t`, `sepol_security_id_t`, null constants, SELinux magic values, and `struct sepol_av_decision`.

Control flow: No logic exists; these types are used by services, policydb, avtab, sidtab, and public APIs.

State and persistence: Access vectors, class IDs, SIDs, and decisions are serialized or returned by policy decision APIs. `sepol_av_decision` carries allowed/decided/audit masks and sequence number.

Dependencies and integration points: Base dependency for most `policydb` headers and service APIs.

Risks: Widths are ABI-sensitive. Changing type sizes would break binary policy parsing and public API compatibility.

Test signals: ABI checks, binary policy read/write, and service decision tests validate these definitions indirectly.
