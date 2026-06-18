# sources/storage-engines/wiredtiger/src/schema/schema_plan.c

Purpose: validates table column definitions and builds compact projection/format plans that map logical table columns to key/value columns in column groups and indexes.

Important APIs and functions: `__wti_schema_colcheck` verifies that named columns match key/value formats. `__wti_table_check` ensures every non-key column appears in a column group. `__wt_struct_plan` builds projection-plan strings. `__wt_struct_reformat` derives a format string for selected columns and optional hidden columns. `__wti_struct_truncate` returns the first N fields of a packing format. Internal helpers `__find_next_col` and `__find_column_format` locate column positions and packing types.

Control flow: column checking counts pack fields from key and value formats, counts configured column names, and rejects mismatches. Table checking skips key columns and verifies each value column can be found in a column group. Plan building iterates requested columns, finds their next matching location, emits column-group/key/value switch markers, skip counts, next/reuse operations, and handles duplicate columns by reusing values. Reformatting walks requested and extra columns, finds original packing types, and adjusts raw item `u`/`U` sizing when moving raw fields between final and non-final positions.

State and persistence behavior: no persistent state is changed. Output is appended into caller-provided `WT_ITEM` buffers and later stored in in-memory table/index plans or metadata-derived format strings.

Dependencies and integration points: used by schema create/open and projection execution. It depends on WiredTiger packing parser helpers, config parsers, table/column-group structures, projection op constants (`WT_PROJ_KEY`, `WT_PROJ_VALUE`, `WT_PROJ_SKIP`, `WT_PROJ_NEXT`, `WT_PROJ_REUSE`), and buffer utilities.

Risks: projection strings are interpreted by `schema_project.c`; any encoding mismatch corrupts cursor key/value packing. Duplicate column names and columns appearing in multiple groups require careful "next match" handling. Raw `u`/`U` conversion is easy to get wrong and can produce incompatible packed values. Empty plans and empty column lists are special cases.

Test signals: complex tables with multiple column groups, duplicate columns, key columns excluded from column-group values, index hidden primary-key columns, raw item fields in middle/end positions, empty projection plans, record-number formats, and round trips through project-in/out/merge/slice.
