# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/opdef.h

`opdef.h` defines the Ghostscript operator-definition catalog interface. Each operator source file declares arrays of `op_def` entries mapping encoded operator names to C `op_proc_t` functions.

An `op_def` contains `oname` and `proc`. Helper macros mark dictionary switches such as `filterdict`, `level2dict`, and `ll3dict`, identify dictionary markers, and terminate a table with an optional initialization procedure. Operator name strings encode the number of operands in the first character.

The header defines a maximum operator-definition table size of 16 entries, requiring large operator files to split definitions into multiple tables. It declares `op_defs_all`, `op_def_count`, `op_find_index`, and helpers to map packed operator refs to catalog indices, operand counts, and C procedures.

It also describes internal `%` operators and the separate global/local `t_oparray` catalogs used for procedure-defined operators. `op_array_table` stores the operator array ref, name-index table, count, base index, attrs, and GC root pointer. `op_index_ref` converts an index back to an operator ref for debugging and packed-array access.
