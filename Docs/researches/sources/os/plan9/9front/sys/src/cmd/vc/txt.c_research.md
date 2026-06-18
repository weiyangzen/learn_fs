# File Research: sources/os/plan9/9front/sys/src/cmd/vc/txt.c

Purpose: MIPS backend initialization, register allocation helpers, address lowering, instruction selection, and target type tables.

Key behavior:
- `ginit` initializes target identity, register state, pseudo nodes, return/safe temporaries, and 64-bit support.
- `gclean` checks leaked registers, emits pending strings/globals, appends `AEND`, and writes object code.
- Provides program allocation (`nextpc`), argument passing (`gargs`, `garg1`), constant/register node constructors, and register allocation/free helpers.
- Converts compiler `Node`s into backend `Adr`s with `naddr`/`raddr`.
- `gmove` selects load, store, register move, integer/FP conversion, unsigned integer to FP fixup, and special FP constants.
- `gopcode` maps generic compiler operations to MIPS opcodes, including multiply/divide LO/HI handling and integer/FP branch generation.
- Provides branch, patch, pseudo-op, small-constant, stack/register-variable, and target type-width/cast tables.

Dependencies:
- Uses all backend structures from `gc.h`, object constants from `v.out.h`, and generic compiler globals.

Notable details:
- Floating-to-integer conversion temporarily changes FP control register rounding unless `fproundflg` allows a simpler path.
- Special double constants are synthesized from dedicated FP constants/registers where possible.
