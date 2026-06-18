# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iname.h

Defines interpreter-facing name-table macros.

Key points:
- Includes `inames.h`.
- Provides convenience macros routed through `mem->gs_lib_ctx->gs_name_table`: `name_memory`, `name_ref`, `name_string_ref`, `name_enter_string`, `name_from_string`, `name_eq`, `name_invalidate_value_cache`, `name_index`, `name_index_ptr`, `name_index_ref`, `name_next_valid_index`, `name_mark_index`, and `name_ref_sub_table`.
- Notes these APIs refer to the interpreter’s distinguished name-table instance.

Research relevance:
- Main include-level access point for interpreter-wide PostScript name handling.
