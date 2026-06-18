## sources/security-integrity/libcap/libcap/cap_flag.c

Purpose: implements in-memory manipulation and comparison of `cap_t` flags and `cap_iab_t` vectors.

Important APIs/functions: `cap_get_flag`, `cap_set_flag`, `cap_clear`, `cap_clear_flag`, `cap_compare`, `cap_fill_flag`, `cap_fill`, `cap_iab_get_vector`, `cap_iab_set_vector`, `cap_iab_fill`, and `cap_iab_compare`.

Control flow: validates opaque object magic, capability indices, flag/vector enums, and requested values; locks objects while reading/writing bitsets; compares cap sets by duplicating one side to avoid lock-order deadlock; IAB vector setters enforce invariants where ambient implies inheritable and clearing inheritable clears ambient.

State/persistence: mutates only heap `cap_t`/`cap_iab_t` objects; no kernel state until other APIs apply them.

Dependencies/integration: internal bit macros from `libcap.h`, cap max bit discovery, public comparison macros `CAP_DIFFERS` and `CAP_IAB_DIFFERS`.

Risks: `cap_set_flag` skips invalid array entries instead of failing after initial validation of count/set/value mode; callers may assume stronger validation. IAB vector semantics are subtle because `CAP_IAB_BOUND` stores bits to drop, not bits to keep.

Test signals: `cap_test` flag fill/compare cases, IAB text/process round trips, invalid enum/index tests, and concurrent access stress for lock behavior.
