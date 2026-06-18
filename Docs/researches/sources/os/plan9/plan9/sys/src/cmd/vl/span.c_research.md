# File Research: sources/os/plan9/plan9/sys/src/cmd/vl/span.c

Address assignment, operand classification, branch-range repair, and optab lookup support for `vl`.

Key responsibilities:
- `span()` assigns final text PCs from `INITTEXT`, computes instruction sizes through `oplook()`, updates text symbol values, and computes `textsize`/`INITDAT`.
- Works around early MIPS 4000 page-boundary delay-slot bugs by inserting a nop before vulnerable branch/jump instructions.
- Rewrites too-far short conditional branches into longer branch-around-jump sequences.
- Optionally places string constants into text.
- `aclass()` maps addresses to codegen classes and computes `instoffset`.
- `oplook()` finds or caches the matching `Optab`.
- `buildop()` sorts and indexes `optab`, creates opcode aliases, and builds fast operand-class cross tables.
- `xdefine()` sets linker symbols if undefined.

Important behavior:
- Extern/static data addressing is biased by `BIG` for small-data addressing.
- `D_CONST` classification distinguishes zero, signed short, unsigned short, upper-half, add, and full long constants.
- Branch class starts as short; long forms are selected or synthesized later.

Risks:
- Class cache invalidation is manual; transformations must call `nocache()`.
- Branch expansion changes the instruction stream while span is iterating.
