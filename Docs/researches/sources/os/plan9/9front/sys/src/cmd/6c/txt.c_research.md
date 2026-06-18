# File Research: sources/os/plan9/9front/sys/src/cmd/6c/txt.c

- Role: Main amd64 code-emission support for 6c: initialization, temporary/register allocation, argument placement, node-to-address lowering, moves/conversions, opcode selection, branches, pseudo-ops, and type sizing.
- `ginit()` initializes target identity, type-class tables, synthetic nodes, string state, program state, and allocatable register sets; reserves SP, temp external registers, and selected XMM/general registers.
- `gclean()` validates register balance, flushes string literals, emits `AGLOBL` for globals/statics, emits `AEND`, and calls `outcode()`.
- `gargs()`/`garg1()` evaluate call arguments, materializing complex function calls into temporaries, placing structures by address, and using `REGARG` for the first register argument where supported.
- Register helpers include `regalloc()`, `regfree()`, `regret()`, `regsalloc()`, `regaalloc()`, `regaalloc1()`, `regialloc()`, and `regind()`.
- `naddr()` translates compiler `Node` forms into `Adr` operands, including registers, indirections, indexed addressing, names, constants, address-of, and constant-offset additions.
- `gmove()` implements load, store, integer widening/narrowing, signed/unsigned conversion, float/integer conversions, float/float moves, zero float constant optimization via XORPD, and unsigned 64-bit to float handling.
- `doindex()` and `gins()` prepare indexed operands and append emitted instructions.
- `gopcode()` maps compiler operators to amd64 opcodes by operand type, including arithmetic, bitwise ops, shifts, rotates, multiply/divide, comparisons, and floating variants.
- `gbranch()`, `patch()`, and `gpseudo()` emit control-flow and pseudo instructions; `exreg()` allocates external register numbers; `ewidth[]` and `ncast[]` define target type sizes and legal casts.
