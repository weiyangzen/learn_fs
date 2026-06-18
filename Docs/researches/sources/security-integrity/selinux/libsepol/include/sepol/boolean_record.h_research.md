# sources/security-integrity/selinux/libsepol/include/sepol/boolean_record.h

Purpose: Declares the opaque public record API for SELinux booleans.

Important APIs and types: Defines opaque `sepol_bool_t` and `sepol_bool_key_t`. Exports key create/unpack/extract/free, compare/compare2, name and value getters/setters, create/clone/free.

Control flow: The API is object-style: create a record or key, mutate fields, pass it to collection APIs in `booleans.h`, then free it.

State and persistence: Records hold name and integer value in implementation-owned heap memory. Persistence occurs only when a record is applied to a `sepol_policydb_t`.

Dependencies and integration points: Depends on `sepol_handle_t` for diagnostics/allocation errors and is consumed by `booleans.c` and external policy manipulation tools.

Risks: Value validity is not enforced by the setter; collection update validates 0/1 later. Callers must manage ownership and free cloned keys/records.

Test signals: Round-trip create/set/clone/free plus policydb query/set tests validate this header.
