# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/inamedef.h

Ghostscript internal name table definition. It ties together name indices, name strings, name references, GC hooks, and save/restore support.

Key behavior:
- Includes `inameidx.h`, `inamestr.h`, `inames.h`, and `gsstruct.h`.
- Caps `EXTEND_NAMES` at 6 extension bits, giving a maximum name-index space derived from `0x10000 << EXTEND_NAMES`.
- Defines `struct name_s`, including `pvalue`, a cached value pointer for global/operator names.
- Defines `name_sub_table` and `name_table_s`, a two-level table of name records and string records.
- Provides inline conversions between name indices, name refs, `name *`, and `name_string_t *`.
- Defines `make_name`, forcing name refs into system VM space so GC can trace them.
- Declares GC/save-restore hooks: `names_unmark_all`, `names_trace_finish`, and `names_restore`.

Notable dependencies:
- `inameidx.h` provides sub-table size and count/index scrambling.
- `inamestr.h` provides string metadata and hash sizing.
- `inames.h` provides public `name_table` API types.

Research notes:
- `pvalue` uses sentinel pointer values `0` and `1`, so code must only treat values above `1` as valid refs through `pv_valid`.
- The inline `names_index_inline` path changes under `EXTEND_NAMES`, deriving high bits from the owning sub-table.
