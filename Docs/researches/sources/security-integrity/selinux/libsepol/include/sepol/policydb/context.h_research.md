# sources/security-integrity/selinux/libsepol/include/sepol/policydb/context.h

Purpose: Defines the internal numeric security-context representation and inline lifecycle/comparison helpers.

Important APIs and types: `context_struct_t` holds user, role, type, and `mls_range_t`. Inline helpers initialize, copy, copy low/high MLS level, compute GLB/LUB, compare, and destroy MLS or full contexts.

Control flow: Public string/record conversion resolves names into numeric values; services and SID tables operate on this compact structure.

State and persistence: The structure stores numeric IDs into policydb value arrays and owns MLS category bitmaps. It is serialized inside ocontexts and SID tables.

Dependencies and integration points: Depends on ebitmap and MLS types; used by context conversion, sidtab, services, and policydb object contexts.

Risks: Copy helpers allocate/copy ebitmaps; partial failure cleanup must be correct. Numeric IDs are one-based and invalid zero values must be rejected by validators.

Test signals: Context copy/destroy, MLS low/high copy, equality, and validation against policydb indexes are key tests.
