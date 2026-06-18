# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iinit.c

Initializes Ghostscript interpreter objects, dictionaries, errors, and operator tables.

Key points:
- Defines dictionary size defaults:
  - `SYSTEMDICT_SIZE`, `SYSTEMDICT_LEVEL2_SIZE`, `SYSTEMDICT_LL3_SIZE`
  - `LEVEL2DICT_SIZE`, `LL3DICT_SIZE`, `FILTERDICT_SIZE`
- Defines `gs_error_names[]` from `ERROR_NAMES`.
- Defines global and local `op_array_table` instances.
- Provides `i_initial_enter_name` and `i_initial_remove_name`.
- Defines initial dictionaries:
  - `level2dict`
  - `ll3dict`
  - `globaldict`
  - `userdict`
  - `filterdict`
- Determines compiled operator language level by scanning `op_defs_all`.
- `gs_have_level2` reports whether Level 2 operators are compiled in.
- `obj_init`:
  - Allocates `systemdict`.
  - Calls `gs_interp_init`.
  - Creates dictionaries referenced by op definitions.
  - Sets up the dictionary stack.
  - Enters dictionaries into `systemdict`.
  - Resets interpreter.
  - Enters `null`, `true`, `false`.
  - Builds `ErrorNames`.
- `zop_init`:
  - Runs initialization procedures embedded in op definition arrays.
  - Enters product/revision/copyright metadata.
- `op_init`:
  - Inserts operator refs into appropriate dictionaries.
  - Skips internal `%` operators and duplicate special-index operators.
  - Allocates global and local op-array tables.
  - Registers op-array tables and name-index tables as GC roots.

Dependencies and interactions:
- Called from `imain.c` during `gs_main_init1/init2`.
- Uses name table, dictionary stack, op definitions, interpreter initialization, and allocator roots.

Research relevance:
- Startup hub that creates the PostScript dictionary/operator environment before init files run.
