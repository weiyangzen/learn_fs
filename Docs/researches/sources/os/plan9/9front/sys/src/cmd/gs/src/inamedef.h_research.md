# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/inamedef.h

Ghostscript internal name-table definition header. It ties together `inameidx.h`, `inamestr.h`, `inames.h`, and GC structure definitions to expose the concrete `name` and `name_table` layouts needed by inline interpreter code.

Key contents:
- Defines name table capacity behavior around `EXTEND_NAMES`, with `max_name_index` and `max_name_count`.
- Defines `struct name_s`, including the cached `pvalue` optimization for names defined only in common dictionaries.
- Defines `pv_no_defn`, `pv_other`, and `pv_valid` markers for cached name-definition state.
- Defines the two-level name table layout: `name_sub_table` blocks and `name_table_s` with allocation/free-list metadata, permanent string count, VM attributes, hash table, memory pointer, and paired name/string subtables.
- Provides inline macros for converting name refs, indices, strings, and table entries: `names_index_string_inline`, `names_string_inline`, `names_index_inline`, `names_index_ptr_inline`, and `names_index_ref_inline`.
- Defines `make_name`, forcing name refs into system VM space so the GC treats name objects as traceable.

Notable dependencies:
- `inameidx.h` for name index/subtable sizing.
- `inamestr.h` for string subtable data.
- `inames.h` for public name-table declarations.
- `gsstruct.h` for `gc_state_t`.

Research notes:
- This is performance-sensitive interpreter infrastructure, not filesystem code.
- The header intentionally exposes implementation internals so interpreter code can inline name/index lookup.
- Extended-name support changes how a ref’s `r_size` field maps back to the full name index, using `high_index` in the subtable when `EXTEND_NAMES` is enabled.
- GC and save/restore integration is explicit through `names_unmark_all`, `names_trace_finish`, and `names_restore`.
