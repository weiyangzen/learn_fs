# File Research: sources/virtualization/spdk/lib/conf/conf.c

Implements SPDK’s legacy INI-style configuration parser. A config is a linked list of sections; each section owns a linked list of items; each item owns a linked list of string values. `spdk_conf_allocate()` creates a config with section merging enabled by default, and `spdk_conf_free()` recursively releases sections, items, values, and the stored filename.

Lookup APIs provide default-config fallback, section iteration, case-insensitive section/key matching, section-prefix matching, section numeric suffix extraction, string value retrieval by key/value index, integer conversion via `spdk_strtol()`, and boolean parsing for Yes/Y/True and No/N/False.

Parsing behavior:
- `[section]` lines create or merge sections and derive `sp->num` from the first digit in the section name.
- parameter lines require a current section, split the key on whitespace or `=`, then split values on whitespace with quote-aware `spdk_strsepq()`.
- `#` comments and blank lines are skipped after leading whitespace.
- lines ending in backslash-newline are concatenated with the next physical line.
- `fgets_line()` grows dynamically for lines longer than the temporary 1024-byte buffer.

The parser logs allocation, syntax, and open errors but continues reading after per-line parse errors. `spdk_conf_set_as_default()` installs the process-wide default config, and `spdk_conf_disable_sections_merge()` preserves duplicate section instances.
