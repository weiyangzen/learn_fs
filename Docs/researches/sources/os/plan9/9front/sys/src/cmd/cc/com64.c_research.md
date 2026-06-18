# File Research: sources/os/plan9/9front/sys/src/cmd/cc/com64.c

Purpose: Rewrites 64-bit integer operations into runtime helper calls on targets that cannot directly implement them.

Key points:
- Declares global `Node*` handles for helper functions such as `_addv`, `_subv`, `_mulv`, `_divv`, `_modv`, shifts, bitwise operations, comparisons, conversions, increments/decrements, and assignment operations.
- `com64init` initializes helper nodes and conversion type codes.
- `com64` detects `vlong`/`uvlong` operands or result types and rewrites operations into `OFUNC` calls unless `machcap` says the target can handle them.
- Handles boolean contexts by calling `_testv`.
- Handles relational operators with signed/unsigned helper variants.
- Handles casts between vlong and smaller integer, pointer, float, and double types.
- Assignment operators are lowered either to specialized mixed vlong/double helpers or the generic `_vasop`.
- `bool64` rewrites vlong expressions in boolean contexts.
- Provides machine-independent conversion helpers `convvtof`, `convftov`, `convftox`, and `convvtox`.

Dependencies and interactions:
- Uses compiler AST constructors, type tables, `machcap`, and `mixedasop` from the front end.
- Runtime helper symbols are marked with `SIGINTERN`.
- Called by target-independent or target-specific lowering paths.

Research notes:
- The file describes itself as common to “64-bit simulating” machines.
- Some conversion comments are marked `BOTCH`, indicating pragmatic rather than fully precise host-independent conversion behavior.
