# sources/security-integrity/audit-userspace/lib/gen_tables64.h

Purpose: Header providing 64-bit lookup helpers and compatibility with the original 32-bit generated table helpers.

Important APIs and types: Declares 32-bit helper prototypes, defines `s2i_64__`, `i2s_64_direct__`, `i2s_64_bsearch__`, `struct transtab64`, and includes `gen_tables.h` for original implementations.

Control flow: 64-bit string-to-int and int-to-string functions use binary/direct search patterns equivalent to `gen_tables.h`, with `int64_t` values. Direct lookup checks value range and casts index to `uint64_t`/`size_t` after bounds checks.

State and persistence: Header-only generated-code support; no mutable state.

Dependencies and integration: Used by `gen_tables64.c` output and includes `<stdint.h>` and `gen_tables.h`.

Risks: Contains inline prototypes before including `gen_tables.h`; compiler compatibility should be checked. Direct lookup guards must prevent overflow when converting `v - min` to an index. The comment has a typo ("Base on") but no functional effect.

Test signals: Compile generated 64-bit and 32-bit tables with strict warnings, exercise direct and bsearch lookup boundaries, and run static analysis for integer conversions.
