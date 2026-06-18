# sources/security-integrity/audit-userspace/lib/gen_tables.c

Purpose: Build-time generator that converts `_S(value, "string")` mapping headers into compact C lookup tables and helper functions.

Important functions: `cmp_value_strings`, `cmp_value_vals`, `cmp_value_orig_index`, `output_strings`, `output_s2i`, `output_i2s`, `output_i2s_transtab`, and `main`. Options include `--i2s`, `--s2i`, `--i2s-transtab`, `--uppercase`, `--lowercase`, and `--duplicate-ints`.

Control flow: Includes the selected `TABLE_H` into a `values[]` array, records original indexes, sorts lexicographically for string tables, emits a packed NUL-separated string blob, optionally emits string-to-int binary-search tables with case normalization, optionally sorts by numeric value and emits either direct-index or binary-search int-to-string tables based on density, and optionally emits `struct transtab` arrays in original order.

State and persistence: No runtime state in the generator. Generated headers are persistent build artifacts and compiled into libaudit.

Dependencies and integration: Built as multiple `gen_*` programs by `lib/Makefile.am` with `CC_FOR_BUILD`. Depends on `gen_tables.h`, audit headers, auparse definitions, and platform constants included for table inputs.

Risks: Uses `assert` for input validation and aborts on duplicates unless allowed. Generated code assumes ASCII for case transforms. Direct table density decisions affect memory footprint. Bad table input breaks build or creates wrong translation behavior.

Test signals: Regenerate all table headers, compare deterministic output, test duplicate handling, case-insensitive lookups, direct versus bsearch generation, and cross-build use of build compiler.
