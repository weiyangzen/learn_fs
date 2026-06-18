# sources/security-integrity/selinux/libsepol/src/mls.h

Purpose: internal MLS header declaring libsepol's MLS parsing, printing, validation, conversion, transition, and user-range setup functions for other policydb components.

Important APIs and types: declares `mls_from_string`, `mls_to_string`, deprecated `mls_compute_context_len`, `mls_sid_to_context`, and `mls_context_to_sid`, plus `mls_context_isvalid`, `mls_convert_context`, `mls_compute_sid`, and `mls_setup_user_range`. It references `sepol_handle_t`, `policydb_t`, `context_struct_t`, `user_datum_t`, and `sepol_security_class_t`.

Control flow: none directly; it defines the callable contract used by context and service code. The declarations distinguish modern string conversion wrappers from deprecated lower-level helpers retained for compatibility inside the library.

State and persistence: no state. The declared functions mutate caller-supplied contexts, writable string pointers, and MLS ranges as described by `mls.c`.

Dependencies and integration points: includes `policydb_internal.h`, public context and policydb headers, and `handle.h`. Used by MLS implementation clients including services, link/expand code, and context conversion paths.

Risks: exposing deprecated helper prototypes internally can perpetuate fragile pointer-buffer semantics. Any signature change would ripple through policydb services and ABI-adjacent internals, though the header itself is not the public installed API.

Test signals: compile coverage should ensure all declarations match definitions and callers. Behavioral tests belong to `mls.c` consumers: context string conversion, transition range computation, and policy conversion.
