# sources/security-integrity/selinux/libsepol/src/context.h

Purpose: Declares internal context conversion and validation helpers implemented by `context.c`.

Important APIs and functions: `context_from_record`, `context_to_record`, `context_from_string`, `context_is_valid`, and `context_to_string`.

Control flow: Internal modules include this header when they need to bridge public `sepol_context_t` records or strings with numeric policydb `context_struct_t`.

State and persistence: No state is owned. Functions allocate returned contexts/records/strings and validate against policydb state.

Dependencies and integration points: Includes `context_internal.h`, internal policydb context and policydb headers, and public handle API. Used by record collection implementations and services.

Risks: API callers must destroy returned `context_struct_t` with `context_destroy` and free memory. Validation requires indexed policydb structures.

Test signals: Internal compile coverage plus public context/record collection tests validate the declarations.
