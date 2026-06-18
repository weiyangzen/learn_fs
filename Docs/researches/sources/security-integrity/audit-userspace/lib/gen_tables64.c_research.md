# sources/security-integrity/audit-userspace/lib/gen_tables64.c

Purpose: 64-bit-capable variant of the lookup-table generator for mapping values that may exceed 32-bit `int`.

Important functions and options: Mirrors `gen_tables.c` and adds `use_64bit` plus `--64bit`. Emits `int64_t` value arrays and lookup functions when 64-bit mode is selected, otherwise emits 32-bit-compatible code with range warnings for out-of-range values.

Control flow: Parses generator options, sorts by string/value/original index, emits packed strings, emits s2i tables using either `s2i__` or `s2i_64__`, emits i2s direct tables only for manageable 64-bit ranges below 1024 entries and density threshold, otherwise emits bsearch tables, and emits 32-bit or 64-bit transtab structures.

State and persistence: Generates persistent C headers for build artifacts; no runtime state beyond local generator flags.

Dependencies and integration: Includes `gen_tables64.h`, `libaudit.h`, `auparse-defs.h`, platform constants, and inttypes support. It is listed in `EXTRA_DIST` in `lib/Makefile.am`; specific Makefile rules in this subset mostly use the 32-bit generator.

Risks: 64-bit direct table generation must avoid enormous sparse arrays, hence the additional range cap. Mixed 32/64 modes can silently truncate if warnings are ignored. Generated headers may require `<inttypes.h>` when using `--64bit`.

Test signals: Generate tables with values around `INT_MAX`, negative 64-bit values, sparse huge ranges, duplicate aliases, and case-normalized string lookups.
