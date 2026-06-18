# sources/security-integrity/selinux/libsepol/include/sepol/booleans.h

Purpose: Declares public policydb collection operations for SELinux booleans.

Important APIs and functions: `sepol_bool_set`, `sepol_bool_count`, `sepol_bool_exists`, `sepol_bool_query`, and `sepol_bool_iterate`. Iterator callbacks return negative for error, positive to stop, or zero to continue.

Control flow: Callers build a key/record with `boolean_record.h`, query or update a `sepol_policydb_t`, and iteration materializes one temporary record per boolean.

State and persistence: `sepol_bool_set` mutates boolean state inside the policydb and triggers conditional rule re-evaluation in the implementation.

Dependencies and integration points: Depends on public policydb, boolean record, and handle APIs; implemented by `src/booleans.c`.

Risks: Boolean changes affect conditional AV rules, so failures during reevaluation can leave callers with an error path to handle. Iterator callbacks must not retain freed temporary records without cloning.

Test signals: Count/existence/query/set plus conditional rule state changes after set are important tests.
