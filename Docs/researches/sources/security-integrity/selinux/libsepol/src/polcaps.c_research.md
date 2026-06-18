# sources/security-integrity/selinux/libsepol/src/polcaps.c

## Purpose
Maps SELinux policy capability numeric ids to CIL/kernel string names and back. This supports policy parsing, CIL generation, and callers that expose policy capabilities by name.

## Important APIs, Types, and Functions
`polcap_names[]` is an indexed table from `POLICYDB_CAP_*` enum values through `POLICYDB_CAP_MAX` to canonical strings. `sepol_polcap_getnum(const char *name)` performs case-insensitive lookup and returns the numeric capability or `-1`. `sepol_polcap_getname(unsigned int capnum)` returns the name or `NULL` for out-of-range or undefined slots.

## Control Flow
Name lookup linearly scans all possible capability slots, skips `NULL` entries, and compares with `strcasecmp`. Number lookup bounds-checks against `POLICYDB_CAP_MAX` and returns the table slot.

## State and Persistence Behavior
The mapping is static read-only process state. No allocation or persistence occurs. Binary persistence is handled elsewhere as ebitmap bits in `policydb->policycaps`; CIL conversion uses this file to emit names.

## Dependencies and Integration Points
Depends on `<sepol/policydb/polcaps.h>` for enum bounds and `<string.h>` for `strcasecmp`. `module_to_cil.c` calls `sepol_polcap_getname()` when emitting `(policycap ...)`, and parsers may call `sepol_polcap_getnum()`.

## Risks and Edge Cases
Adding a new `POLICYDB_CAP_*` requires updating this table or lookups will return `NULL`/`-1`. String matching is case-insensitive but does not normalize punctuation or aliases. Unknown set bits cause CIL conversion to fail when `getname()` returns `NULL`.

## Test Signals
Tests should assert every defined policycap enum has a non-null name, round-trip name-to-number-to-name for all entries, case-insensitive lookup, out-of-range `getname()` behavior, and failure behavior for unknown names.
