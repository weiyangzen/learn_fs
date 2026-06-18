# File Research: sources/os/plan9/9front/sys/src/cmd/5c/peep.c

This file implements ARM peephole and local CFG optimizations over the `Reg` graph.

Main optimization flow:
- `peep()` fills missing `Reg` nodes between optimizer graph nodes, then repeatedly applies:
  - shift folding into later `D_SHIFT` operands,
  - constant propagation,
  - register copy propagation,
  - substitution propagation,
  - redundant sign/zero-extension move removal,
  - `EOR $-1,x,y` to `MVN x,y`,
  - extra ARM addressing modes for pre/post-indexed loads/stores,
  - `CMP $0,R` elimination by setting the CPSR on a prior producer,
  - short conditional predication.
- `excise()` turns an instruction into `ANOP`.

Copy and constant propagation:
- `uniqp()`/`uniqs()` identify unique predecessor/successor cases.
- `subprop()` swaps registers backward to enable copy elimination.
- `copyprop()` and recursive `copy1()` remove redundant register moves across simple CFG paths.
- `constprop()` substitutes register-held constants into subsequent moves.

Shift/address-mode optimization:
- `shiftprop()` folds standalone `ASLL`/`ASRL`/`ASRA`/`AROR` into a later data-processing instruction’s `D_SHIFT` source operand when safe.
- `findpre()`, `findinc()`, `nochange()`, `finduse()`, and `xtramodes()` detect address increments suitable for ARM pre-indexing, post-indexing, register offset, scaled-register offset, and immediate offset modes.

Use/set modeling:
- `copyu()` classifies or substitutes operand use for each opcode: unused, used, read-alter-rewrite, set, or set-and-used.
- Handles multiply-long, `MOVM`, moves, arithmetic, branches, returns, calls, and text pseudo ops.
- `copyas()`, `copyau()`, `copyau1()`, `copysub()`, and `copysub1()` implement direct/indirect matching and substitution.

Predication:
- `predinfo[]` maps branch opcodes to true/false condition codes and inverted opcodes.
- `isbranch()`, `predicable()`, and `modifiescpsr()` classify instructions.
- `joinsplit()` finds short instruction chains that can be predicated.
- `applypred()` applies condition codes and removes or rewrites branches.
- `predicate()` transforms short if/else-like control flow into predicated instruction sequences.

Dependencies and interactions:
- Depends on accurate CFG built by `reg.c`.
- Uses opcode ordering from `5.out.h`, especially contiguous conditional branches.
- Called from `regopt()` after global register allocation.

Research relevance:
- Major final code-quality stage for ARM codegen.

Risk notes:
- `copyu()` is semantic infrastructure; missing an opcode or misclassifying use/set can produce wrong-code.
- Predication is limited to short chains and avoids instructions that set CPSR or are unsupported by linker-emulated ops.
- Address-mode folding must avoid changing base registers before later uses.
