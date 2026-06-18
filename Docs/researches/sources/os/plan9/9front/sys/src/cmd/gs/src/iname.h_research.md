# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iname.h

Defines interpreter-facing name-table macros.

Key points:
- Includes `inames.h`.
- Provides convenience macros that route through `mem->gs_lib_ctx->gs_name_table`:
  - `name_memory`
  - `name_ref`
  - `name_string_ref`
  - `name_enter_string`
  - `name_from_string`
  - `name_eq`
  - `name_invalidate_value_cache`
  - `name_index`
  - `name_index_ptr`
  - `name_index_ref`
  - `name_next_valid_index`
  - `name_mark_index`
  - `name_ref_sub_table`
- Notes these APIs refer to the interpreter’s distinguished name-table instance.

Dependencies and interactions:
- Used by most interpreter code that needs name lookup or name/string conversion.
- Wraps lower-level `names_*` APIs implemented in `iname.c`.

Research relevance:
- Main include-level access point for interpreter-wide PostScript name handling.
