# File Research: sources/os/plan9/9front/sys/src/cmd/awk/parse.c

Implements parse-tree construction helpers for awk.

Key responsibilities:
- Allocates variable-sized `Node` structures.
- Provides `node1` through `node4` and statement/expression wrappers `stat1..stat4`, `op1..op4`.
- Converts `Cell` objects to value nodes.
- Builds `$0` references with `rectonode`.
- Converts scalar cells into arrays on demand with `makearr`.
- Builds pattern-range state nodes with `pa2stat`.
- Links statement lists with `linkum`.
- Registers function definitions and records argument counts.
- Looks up function argument indexes.
- Provides pointer/integer conversion helpers for embedding small integers in `Node*` fields.

Important interfaces:
- Used heavily by `awkgram.y`.
- Uses globals `lineno`, `exitstatus`, `paircnt`, `pairstack`, and parser globals `arglist`.

Notes:
- Limits `pat,pat` range patterns to `PA2NUM` 50.
