# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iinit.c

Initializes Ghostscript interpreter objects, dictionaries, errors, and operator tables.

Key points:
- Defines dictionary size defaults for `systemdict`, `level2dict`, `ll3dict`, and `filterdict`.
- Defines `gs_error_names[]` from `ERROR_NAMES`.
- Defines global and local `op_array_table` instances.
- Provides `i_initial_enter_name` and `i_initial_remove_name`.
- Defines initial dictionaries: `level2dict`, `ll3dict`, `globaldict`, `userdict`, and `filterdict`.
- Determines compiled operator language level by scanning `op_defs_all`; `gs_have_level2` reports whether Level 2 operators are compiled in.
- `obj_init` allocates `systemdict`, initializes the interpreter, creates dictionaries referenced by op definitions, sets up the dictionary stack, enters dictionaries and booleans/null into `systemdict`, and builds `ErrorNames`.
- `zop_init` runs initialization procedures embedded in op definition arrays and enters product/revision/copyright metadata.
- `op_init` inserts operator refs into dictionaries, skips internal `%` operators and duplicate special-index operators, allocates global/local op-array tables, and registers them as GC roots.

Research relevance:
- Startup hub that creates the PostScript dictionary/operator environment before init files run.
