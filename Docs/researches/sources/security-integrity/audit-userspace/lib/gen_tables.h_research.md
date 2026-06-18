# sources/security-integrity/audit-userspace/lib/gen_tables.h

Purpose: Header emitted into/used by generated 32-bit lookup table code.

Important APIs and types: Defines ASCII helpers `GT_ISUPPER` and `GT_ISLOWER`, inline lookup functions `s2i__`, `i2s_direct__`, `i2s_bsearch__`, and `struct transtab`.

Control flow: `s2i__` performs binary search over sorted string offsets and integer values, reusing previously matched prefix lengths. `i2s_direct__` indexes a dense table by `v - min`. `i2s_bsearch__` binary-searches sorted integer tables.

State and persistence: Header-only helpers compiled into generated table consumers.

Dependencies and integration: Included by `gen_tables.c` output and by `gen_tables64.h` for 32-bit compatibility. Used indirectly by libaudit translation functions.

Risks: Functions use `ssize_t` but include only standard size headers here; consumers must compile in an environment where it is available. Binary search relies on generated sorted tables. Direct table offsets use `-1u` sentinel.

Test signals: Unit tests for successful/missing string lookups, dense and sparse int lookups, boundary min/max values, and alias behavior.
