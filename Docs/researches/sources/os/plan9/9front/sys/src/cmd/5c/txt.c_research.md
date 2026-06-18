# File Research: sources/os/plan9/9front/sys/src/cmd/5c/txt.c

This file initializes and finalizes ARM code generation, manages registers and temporaries, maps AST nodes to object operands, emits moves/opcodes/branches/pseudo ops, and defines target type widths/cast compatibility.

Initialization/finalization:
- `ginit()` sets ARM target identity, initializes listing formats, zero `zprog`, constant/register template nodes, `.safe` and `.ret` nodes, 64-bit support, and reserved registers.
- Reserved registers include `REGTMP`, `REGSB`, `REGSP`, `REGLINK`, `REGPC`, and two external registers.
- `gclean()` checks leaked registers, flushes string data, emits `AGLOBL` for globals/statics, emits `AEND`, and calls `outcode()`.

Instruction and argument construction:
- `nextpc()` appends a zeroed `Prog` and advances `pc`.
- `gargs()`/`garg1()` evaluate function arguments, precomputing complex arguments to safe temporaries, passing first scalar argument in `REGARG`, and placing others on stack.
- `nodconst()`, `nod32const()`, `nodfconst()`, `nodreg()`, and `regret()` build reusable node templates.

Register/temp allocation:
- `tmpreg()` finds a free integer temp.
- `regalloc()` allocates integer, floating, or register-pair temps.
- `regialloc()`, `regfree()`, `regsalloc()`, `regaalloc1()`, `regaalloc()`, and `regind()` support pointer temps, safe stack temps, argument registers, argument stack slots, and indirect register nodes.
- `exreg()` reserves external integer/floating registers.

Addressing:
- `raddr()` extracts a register operand into a `Prog.reg`.
- `naddr()` maps AST nodes to `Adr` forms for registers, indirects, names, constants, address-of, and constant addition.

Move and opcode emission:
- `gmovm()` emits `AMOVM` with increment/writeback flags.
- `gmove()` handles loads, stores, type conversions, 64-bit register-pair moves, integer/floating conversions, sign/zero extension, and unsigned-to-float conversion via a correction sequence.
- `gmover()` emits narrower sign/zero-extending moves for relational conversion cases.
- `gins()` emits raw opcodes.
- `gopcode()` maps C ops to ARM opcodes, including arithmetic, shifts, rotate, calls, multiply/divide/mod, comparisons, `ACMP`/`ACMN`, conditional branches, and `ACASE`.
- `gbranch()` emits `ARET` or `AB`.
- `patch()` fills branch target offsets.
- `gpseudo()` emits `ATEXT`, `ADATA`, and `AGLOBL` pseudo instructions.

Utility/type tables:
- `samaddr()` suppresses redundant register-pair/self moves.
- `sconst()` and `sval()` classify constants.
- `ewidth[]` defines target type widths.
- `ncast[]` defines native cast compatibility sets.

Dependencies and interactions:
- Called throughout `cgen.c`, `swt.c`, `reg.c`, and common compiler flow.
- Emits `Prog` chains later optimized by `regopt()` and serialized by `outcode()`.

Research relevance:
- This is the low-level instruction emission layer and target ABI configuration for `5c`.

Risk notes:
- `gmove()` contains many type-crossing cases; missing a conversion leads to `bad opcode in gmove`.
- Register-pair allocation order is normalized so low/high words are stable.
- Unsigned integer to float conversion emits multi-instruction code and branch patching, so it is sensitive to register lifetimes.
