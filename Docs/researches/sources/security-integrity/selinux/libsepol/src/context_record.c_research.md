# sources/security-integrity/selinux/libsepol/src/context_record.c

Purpose: Implements the opaque public `sepol_context_t` record API and string parsing/formatting.

Important APIs and functions: User/role/type/MLS getters and setters, `sepol_context_create`, `sepol_context_clone`, `sepol_context_free`, `sepol_context_from_string`, and `sepol_context_to_string`.

Control flow: Setters duplicate incoming strings and replace owned fields. Clone deep-copies all required fields and optional MLS. `from_string` accepts `"<<none>>"` as a null context, otherwise splits `user:role:type[:mls]`. `to_string` computes size with overflow checks and formats with `snprintf`.

State and persistence: `struct sepol_context` owns four heap strings. No policydb validation or persistence occurs here.

Dependencies and integration points: Uses public context headers through `context_internal.h`, debug/private helpers, and libc. Higher-level `context.c` validates records against policydb.

Risks: Clone assumes user/role/type are non-null. Parsing treats everything after the third colon as MLS, so malformed extra-colon MLS validation is deferred.

Test signals: Round-trip strings with/without MLS, `"<<none>>"`, malformed strings, clone deep copy, overflow/error paths, and free-on-null validate behavior.
