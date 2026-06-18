# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/opdef.h

## Purpose
Operator definition/catalog interface for Ghostscript’s PostScript interpreter.

## Main Structure
- Defines `op_def` entries with operator name string and C procedure pointer.
- Provides macros for dictionary-bound operator tables and table terminators.
- Defines fixed table chunk size: `OP_DEFS_LOG2_MAX_SIZE=4`, `OP_DEFS_MAX_SIZE=16`.
- Declares global `op_defs_all` and `op_def_count`.
- Defines operator index helpers for normal operators and internal `%` operators.
- Defines `op_array_table` for procedure-defined operators in global/local tables.
- Declares `op_index_ref`.

## Integration Notes
- Operator source files declare arrays ending with `op_def_end(iproc)`.
- Makefiles must split any operator definition table over 16 entries into multiple tables and multiple `-oper` entries.
- Supports separate dictionaries such as `filterdict`, `level2dict`, and `ll3dict`.

## Risks and Edge Cases
- Operator table size limit is structural and enforced by build/source organization, not dynamic allocation.
- Internal operators have packed size 0 and require lookup by procedure address.
- Correct indexing is central to `bind`, packed arrays, and operator execution behavior.
